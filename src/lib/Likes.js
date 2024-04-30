import axios from "axios";
import {getBasicHeaderValue, getUser} from "./User";
import {isString} from "lodash";

export async function getLikes(url) {
    try {
        const response = await axios.get(url, {});
        const likesCount = response.data.items.length;
        return likesCount;

    } catch (error) {
        throw error;
    }
}

export async function postLike(url, body) {
    try {
        const user = getUser()
        const data = {
            id: user.id,
            ...body,
        }
        const response = await axios.post(url, data, {
            headers: { Authorization: getBasicHeaderValue() },
        });
        return true;

    } catch (error) {
        if (error.response && error.response.status === 409){
            return false;
        } else {
            throw error;
        }
    }
}


export async function likeSubmit(authorId, postId, comment = undefined) {
    let body = {};
    if (comment !== undefined && !isString(comment)) {
        body = {commentAuthorUrl: comment.author.id};
    }
    let commentId = comment?.id.split("/").pop();
    let likeUrl = `/api/authors/${authorId}/posts/${postId}${commentId !== undefined ? `/comments/${commentId}` : ""}/likes`;


    try {
        const liked = await postLike(likeUrl, body);
        // Fetch updated likes count after successful like
        const likeCount = await getLikes(likeUrl);
        return [liked, likeCount];
    } catch (error) {
        console.error('Failed to submit like:', error);
    }
}
