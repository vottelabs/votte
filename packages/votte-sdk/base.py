import os
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, ClassVar, Generic, Literal, Self, TypeVar

import requests
from loguru import logger
from pydantic import BaseModel

from notte_sdk.errors import AuthenticationError, NotteAPIError, NotteAPIExecutionError

TResponse = TypeVar("TResponse", bound=BaseModel, covariant=True)


class NotteEndpoint(BaseModel, Generic[TResponse]):
    path: str
    response: type[TResponse]
    request: BaseModel | None = None
    method: Literal["GET", "POST", "DELETE"]
    params: BaseModel | None = None

    def with_request(self, request: BaseModel) -> Self:
        # return deep copy of self with the request set
        """
        Return a deep copy of the endpoint with the specified request.

        Creates a new instance of the endpoint with its request attribute updated to the provided model.
        The original instance remains unmodified.

        Args:
            request: A Pydantic model instance carrying the request data.

        Returns:
            A new endpoint instance with the updated request.
        """
        return self.model_copy(update={"request": request})

    def with_params(self, params: BaseModel) -> Self:
        # return deep copy of self with the params set
        """
        Return a new endpoint instance with updated parameters.

        Creates a copy of the current endpoint with its "params" attribute set to the provided
        Pydantic model.

        Args:
            params: A Pydantic model instance containing the new parameters.
        """
        return self.model_copy(update={"params": params})


class BaseClient(ABC):
    DEFAULT_NOTTE_API_URL: ClassVar[str] = "https://api.notte.cc"
    DEFAULT_REQUEST_TIMEOUT_SECONDS: ClassVar[int] = 60

    def __init__(
        self,
        base_endpoint_path: str | None,
        api_key: str | None = None,
        verbose: bool = False,
    ):
        """
        Initialize a new API client instance.

        Sets up the client by resolving an API key from the provided parameter or the
        NOTTE_API_KEY environment variable. Selects the server URL (defaulting to a
        preconfigured server if none is provided), initializes a mapping of endpoints
        using the implemented 'endpoints' method, and stores an optional base endpoint
        path for constructing request URLs.

        Args:
            base_endpoint_path: Optional base path to be prefixed to endpoint URLs.
            api_key: Optional API key for authentication; if not supplied, retrieved from
                the NOTTE_API_KEY environment variable.

        Raises:
            AuthenticationError: If an API key is neither provided nor available in the environment.
        """
        token = api_key or os.getenv("NOTTE_API_KEY")
        if token is None:
            raise AuthenticationError("NOTTE_API_KEY needs to be provided")
        self.token: str = token
        if os.getenv("NOTTE_API_URL") is not None and os.getenv("NOTTE_API_URL") != self.DEFAULT_NOTTE_API_URL:
            logger.warning(f"Custom NOTTE_API_URL is set: {os.getenv('NOTTE_API_URL')}")
        self.server_url: str = os.getenv("NOTTE_API_URL") or self.DEFAULT_NOTTE_API_URL
        self._endpoints: dict[str, NotteEndpoint[BaseModel]] = {
            endpoint.path: endpoint for endpoint in self.endpoints()
        }
        self.base_endpoint_path: str | None = base_endpoint_path
        self.verbose: bool = verbose

    @staticmethod
    @abstractmethod
    def endpoints() -> Sequence[NotteEndpoint[BaseModel]]:
        """
        Return API endpoints for the client.

        This abstract method should be implemented by subclasses to supply the list of available
        NotteEndpoint instances for the client.

        Returns:
            Sequence[NotteEndpoint[BaseModel]]: A list of endpoints for the client.
        """
        pass

    def headers(self) -> dict[str, str]:
        """
        Return HTTP headers for authenticated API requests.

        Constructs and returns a dictionary containing the 'Authorization' header,
        which is formatted as a Bearer token using the API key stored in self.token.
        """
        return {"Authorization": f"Bearer {self.token}"}

    def request_path(self, endpoint: NotteEndpoint[TResponse]) -> str:
        """
        Constructs the full request URL for the given API endpoint.

        If a base endpoint path is defined, the URL is formed by concatenating the server URL,
        the base endpoint path, and the endpoint's path. Otherwise, the endpoint's path is appended
        directly to the server URL.
        """
        if self.base_endpoint_path is None:
            return f"{self.server_url}/{endpoint.path}"
        return f"{self.server_url}/{self.base_endpoint_path}/{endpoint.path}"

    def _request(self, endpoint: NotteEndpoint[TResponse]) -> requests.Response:
        """
        Executes an HTTP request for the given API endpoint.

        Constructs the full URL and headers from the endpoint's configuration and issues an HTTP
        request using the specified method (GET, POST, or DELETE). For POST requests, a request model
        must be provided; otherwise, a ValueError is raised. If the response status code is not 200 or
        the JSON response contains an error detail, a NotteAPIError is raised.

        Args:
            endpoint: An API endpoint instance containing the HTTP method, path, optional request model,
                and query parameters.

        Returns:
            The JSON-decoded response from the API.

        Raises:
            ValueError: If a POST request is attempted without a request model.
            NotteAPIError: If the API response indicates a failure.
        """
        headers = self.headers()
        url = self.request_path(endpoint)
        params = endpoint.params.model_dump() if endpoint.params is not None else None
        if self.verbose:
            logger.info(f"Making `{endpoint.method}` request to `{endpoint.path} (i.e `{url}`) with params `{params}`.")
        match endpoint.method:
            case "GET":
                response = requests.get(
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=self.DEFAULT_REQUEST_TIMEOUT_SECONDS,
                )
            case "POST":
                if endpoint.request is None:
                    raise ValueError("Request model is required for POST requests")
                response = requests.post(
                    url=url,
                    headers=headers,
                    json=endpoint.request.model_dump(),
                    params=params,
                    timeout=self.DEFAULT_REQUEST_TIMEOUT_SECONDS,
                )
            case "DELETE":
                response = requests.delete(
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=self.DEFAULT_REQUEST_TIMEOUT_SECONDS,
                )
        if response.status_code != 200:
            if response.headers.get("x-error-class") == "NotteApiExecutionError":
                raise NotteAPIExecutionError(path=f"{self.base_endpoint_path}/{endpoint.path}", response=response)

            raise NotteAPIError(path=f"{self.base_endpoint_path}/{endpoint.path}", response=response)
        response_dict: Any = response.json()
        if "detail" in response_dict:
            raise NotteAPIError(path=f"{self.base_endpoint_path}/{endpoint.path}", response=response)
        return response_dict

    def request(self, endpoint: NotteEndpoint[TResponse]) -> TResponse:
        """
        Requests the specified API endpoint and returns the validated response.

        This method sends an HTTP request according to the endpoint configuration and
        validates that the response is a dictionary. It then parses the response using the
        endpoint's associated response model. If the response is not a dictionary, a
        NotteAPIError is raised.

        Args:
            endpoint: The API endpoint configuration containing request details and the
                      expected response model.

        Returns:
            The validated response parsed using the endpoint's response model.

        Raises:
            NotteAPIError: If the API response is not a dictionary.
        """
        response: Any = self._request(endpoint)
        if not isinstance(response, dict):
            raise NotteAPIError(path=f"{self.base_endpoint_path}/{endpoint.path}", response=response)
        return endpoint.response.model_validate(response)

    def request_list(self, endpoint: NotteEndpoint[TResponse]) -> Sequence[TResponse]:
        # Handle the case where TResponse is a list of BaseModel
        """
        Retrieves and validates a list of responses from the API.

        This method sends a request using the provided endpoint and expects the response to be a list. Each item is validated
        against the model defined in the endpoint. A NotteAPIError is raised if the response is not a list.

        Parameters:
            endpoint: The API endpoint containing the path and the expected response model.

        Returns:
            A list of validated response items.

        Raises:
            NotteAPIError: If the response is not a list.
        """
        response_list: Any = self._request(endpoint)
        if not isinstance(response_list, list):
            if "items" in response_list:
                response_list = response_list["items"]
            if not isinstance(response_list, list):
                raise NotteAPIError(path=f"{self.base_endpoint_path}/{endpoint.path}", response=response_list)
        return [endpoint.response.model_validate(item) for item in response_list]  # pyright: ignore[reportUnknownVariableType]

    def _request_file(
        self, endpoint: NotteEndpoint[TResponse], file_type: str, output_file: str | None = None
    ) -> bytes:
        url = self.request_path(endpoint)
        response = requests.get(
            url=url,
            headers=self.headers(),
            timeout=self.DEFAULT_REQUEST_TIMEOUT_SECONDS,
        )
        if b"not found" in response.content:
            raise ValueError("Replay is not available.")

        if output_file is not None:
            if not output_file.endswith(f".{file_type}"):
                raise ValueError(f"Output file must have a .{file_type} extension.")
            with open(output_file, "wb") as f:
                _ = f.write(response.content)
        return response.content
