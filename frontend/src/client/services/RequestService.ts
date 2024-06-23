import type { CancelablePromise } from "../core/CancelablePromise";
import { FriendRequests } from "../models";
import { request as __request } from '../core/request';
import { OpenAPI } from '../core/OpenAPI';

export class RequestService {
  /**
   * Read Requests to me
   * Retrieve Friend Requests for me.
   * @returns UsersPublic Successful Response
   * @throws ApiError
   */
  public static getRequests(): CancelablePromise<FriendRequests> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/api/v1/friend/requests-me",
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
