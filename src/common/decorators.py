import logging
import os
import random
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Protocol, Type, TypeVar, cast

import httpx
import requests
import sentry_sdk

F = TypeVar("F", bound=Callable[..., Any])


class ResponseLike(Protocol):
    status_code: int
    headers: dict[str, Any]


class ExceptionWithResponse(Protocol):
    response: ResponseLike


DEFAULT_VERBOSE = os.getenv("FUNCTION_TARGET") is None


def routine(tag: str, verbose: bool = DEFAULT_VERBOSE) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = datetime.now().timestamp()

            logging_level = logging.getLogger().getEffectiveLevel()

            try:
                logging.info(f"\n\033[33m[] Starting\033[0m : {tag} :  {func.__name__}")

                if not verbose:
                    logging.getLogger().setLevel(logging.CRITICAL)

                outputs = func(*args, **kwargs)

                logging.getLogger().setLevel(logging_level)

                completion = int(datetime.now().timestamp() - start_time)

                logging.info(f"\n\033[32m[] Success\033[0m : {completion}s")

                for output in outputs:
                    logging.info(
                        f"    \033[31m[+] Summary\033[0m : {output[0]} ({output[1]} rows)"
                    )

            except Exception as exception:
                logging.getLogger().setLevel(logging_level)

                logging.info(f"\033m[] Failure\033[0m : {tag} : {func.__name__}")

                if verbose:
                    raise exception
                else:
                    sentry_sdk.capture_exception(exception)

            finally:
                logging.info("")

        return cast(F, wrapper)

    return decorator


def retry(
    attempts: int = 5,
    base_delay: float = 1.0,
    factor: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    exceptions: tuple[Type[Exception], ...] = (
        requests.exceptions.RequestException,
        httpx.RequestError,
        httpx.HTTPStatusError,
        ConnectionError,
        TimeoutError,
    ),
    respect_retry_after: bool = True,
    on_retry: Callable[[Exception, int], None] | None = None,
    calls_per_second: float | None = None,
    burst_size: int | None = None,
) -> Callable[[F], F]:
    if calls_per_second is not None and burst_size is None:
        burst_size = int(calls_per_second)

    last_called = [0.0] if calls_per_second else None
    available_tokens = [float(burst_size)] if burst_size else None

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_time = time.time()
            time_passed = current_time - last_called[0]

            if burst_size is not None:
                available_tokens[0] = min(
                    float(burst_size),
                    available_tokens[0] + time_passed * calls_per_second,
                )

            if available_tokens[0] < 1:
                sleep_time = (1 - available_tokens[0]) / calls_per_second
                logging.debug(f"Rate limit reached, sleeping for {sleep_time:.3f}s")
                time.sleep(sleep_time)
                available_tokens[0] = 1

            available_tokens[0] -= 1
            last_called[0] = time.time()

            last_exception = None

            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == attempts:
                        break

                    delay = base_delay

                    if isinstance(e, requests.exceptions.HTTPError):
                        if e.response.status_code == 429:
                            if (
                                respect_retry_after
                                and "Retry-After" in e.response.headers
                            ):
                                try:
                                    delay = float(e.response.headers["Retry-After"])
                                except (ValueError, TypeError):
                                    delay = base_delay * (3 ** (attempt - 1))
                            else:
                                delay = base_delay * (3 ** (attempt - 1))
                        elif e.response.status_code >= 500:
                            delay = base_delay * (factor ** (attempt - 1))

                        elif e.response.status_code == 403:
                            raise

                        else:
                            delay = base_delay * attempt

                    elif isinstance(e, requests.exceptions.Timeout):
                        delay = base_delay * attempt

                    elif isinstance(e, (requests.exceptions.ConnectionError, httpx.HTTPStatusError, httpx.ConnectError)):
                        delay = base_delay * (factor ** (attempt - 1))

                    else:
                        response = getattr(e, "response", None)
                        if response is not None and hasattr(response, "status_code"):
                            exc_with_response = cast(ExceptionWithResponse, e)

                            if exc_with_response.response.status_code == 429:
                                if respect_retry_after:
                                    retry_after = (
                                        exc_with_response.response.headers.get(
                                            "Retry-After"
                                        )
                                    )
                                    if retry_after:
                                        try:
                                            delay = float(retry_after)
                                        except (ValueError, TypeError):
                                            delay = base_delay * (factor**attempt)

                                    else:
                                        delay = base_delay * (factor**attempt)

                                else:
                                    delay = base_delay * (factor**attempt)

                            elif exc_with_response.response.status_code >= 500:
                                delay = base_delay * (factor ** (attempt - 1))

                            else:
                                delay = base_delay * (factor**attempt)

                        else:
                            delay = base_delay * (factor ** (attempt - 1))

                    delay = min(delay, max_delay)

                    if jitter:
                        delay += random.uniform(0, base_delay)

                    error_msg = str(e)
                    if hasattr(e, "response"):
                        exc_with_response = cast(ExceptionWithResponse, e)
                        if hasattr(exc_with_response.response, "status_code"):
                            error_msg = f"HTTP {exc_with_response.response.status_code}: {error_msg}"

                    logging.warning(
                        f"Attempt {attempt}/{attempts} failed for {func.__name__}: "
                        f"{type(e).__name__}: {error_msg}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    if on_retry:
                        on_retry(e, attempt)

                    time.sleep(delay)

                except Exception as e:
                    logging.error(
                        f"Non-retryable exception in {func.__name__}: "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    raise

            if last_exception:
                logging.error(
                    f"Retry decorator exhausted all {attempts} attempts for {func.__name__}"
                )
                raise last_exception

            raise RuntimeError(
                f"Retry decorator exhausted all attempts without capturing an exception in {func.__name__}"
            )

        return cast(F, wrapper)

    return decorator
