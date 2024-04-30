import {fetchLocalWithBasic, MakeUrl} from "./Url";
import {getUser} from "./User";

export async function inboxDelete() {
    return await fetchLocalWithBasic(`/authors/${getUser().id}/inbox`, {method: "DELETE"});
}

export async function inboxGet() {
    let notifications = [];
    let shouldContinue = true;

    const pageSize = 10;
    const userId = getUser().id;
    const fetcher = page => fetchLocalWithBasic(`/authors/${userId}/inbox?page=${page}&size=${pageSize}`)
        .then(response => response.json())
        .then(data => data.items);

    let page = 1;
    while (shouldContinue) {
        const items = await fetcher(page);
        notifications = notifications.concat(items);
        shouldContinue = items.length === pageSize;
    }
    return notifications;
}

export async function foreignFollowGet(authorId, targetUrl) {
    let encodedUrl = encodeURI(targetUrl);
    return await fetchLocalWithBasic(`/authors/${authorId}/followers/${encodedUrl}`);
}

export async function foreignFollowPut(targetUrl) {
    let encodedUrl = encodeURI(targetUrl);
    return await fetchLocalWithBasic(`/authors/${getUser().id}/followers/${encodedUrl}`, {method: "PUT"});
}

export async function foreignFollowDelete(master_id, followerUrl) {
    let encodedUrl = encodeURI(followerUrl);
    return await fetchLocalWithBasic(`/authors/${master_id}/followers/${encodedUrl}`, {method: "DELETE"})
}

/**
 * Delete a request from the inbox of the current user.
 * @param targetUrl The url of the author who is requesting.
 * @returns {Promise<Response>}
 */
export async function requestDelete(targetUrl) {
    let encodedUrl = encodeURI(targetUrl);
    return await fetchLocalWithBasic(`/ext/requests/${encodedUrl}`, {method: "DELETE"});
}

export async function inboxPost(data, authorId) {
    const url = `/authors/${authorId}/inbox`;

    return await fetchLocalWithBasic(url, {
        method: "POST", headers: {"Content-Type": "application/json",}, body: JSON.stringify(data),
    });
}