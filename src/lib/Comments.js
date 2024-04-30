import axios from "axios";
import { getBasicHeaderValue } from "./User";

export async function getComments(url) {
    try {
        const response = await axios.get(url, {});
        return response;
    } catch (error) {
        console.error('Failed to get comments:', error);
        throw error;
    }
}

export async function postComment(comment, url) {
    try {
        const response = await axios.post(url, {
            comment: comment,
            contentType: "text/markdown"
        }, {
            headers: { Authorization: getBasicHeaderValue() },
        });
        return response;
    } catch (error) {
        throw error;
    }

}