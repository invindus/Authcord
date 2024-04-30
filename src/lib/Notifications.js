import axios from "axios";

export async function postCommentNotification(authorId, response) {
    try {
        const notificationResponse = await axios.post(`/api/authors/${authorId}/inbox`, {
            content: response.data,
        }, {
            headers: { 'Content-Type': 'application/json' }
        });
        return notificationResponse;

    } catch (error) {
        console.error('Failed to send notification:', error);
        return null;
    }
}

export async function postLikeNotification(authorId, content) {
    try {
        const notificationResponse = await axios.post(`/api/authors/${authorId}/inbox`, {content}, {
            headers: { 'Content-Type': 'application/json' }
        });
        return notificationResponse;

    } catch (error) {
        console.error('Failed to send notification:', error);
        throw error;
    }
}
