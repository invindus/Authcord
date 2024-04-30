import axios from "axios";
import {getBasicHeaderValue} from "./User";
import {getComments} from "./Comments";
import {getLikes} from "./Likes";
import {fetchLocalWithBasic} from "./Url";

export async function getSinglePost(authorId, postId) {
    const postUrl = `/api/authors/${authorId}/posts/${postId}`;

    try {
        const response = await axios.get(postUrl, {
            headers: {Authorization: getBasicHeaderValue()},  // for friends only posts
        });
        const dataAuthorId = response.data.author.id.split("/").pop();
        const dataPostId = response.data.id.split("/").pop();

        const commentsUrl = `/api/authors/${dataAuthorId}/posts/${dataPostId}/comments?page=1&size=40`;
        const commentsResponse = await getComments(commentsUrl);

        const likesUrl = `/api/authors/${dataAuthorId}/posts/${dataPostId}/likes`;
        const likesCount = await getLikes(likesUrl);

        return [response, commentsResponse, likesCount];
    } catch (error) {
        throw error;
    }
}

export async function getPosts(currentPage, pageSize) {
    const postsUrl = `/posts/?page=${currentPage}&size=${pageSize}`;
    try {
        return await fetchLocalWithBasic(postsUrl)
            .then(r => r.json());
    } catch (error) {
        console.error("Failed to fetch posts:", error);
        return null;
    }
}

// Return post response to current author's posts
export async function postData(authorId, formData) {
    const postsUrl = `/api/authors/${authorId}/posts/`;
    try {
        let response = await axios.post(postsUrl, formData, {
            headers: {Authorization: getBasicHeaderValue()},
        });
        return response;
    } catch (error) {
        console.error("Failed to create post:", error);
        return null;
    }
}

// After posting to current author's posts, share to follower's inbox
// Used in Feed, PostPage
export async function shareToFollowers(authorId, postResponse) {
    try {

        let followerList = await axios.get(`/api/authors/${authorId}/followers`, {headers: {Authorization: getBasicHeaderValue()}});

    


        followerList.data.items.forEach(async (follower) => {
            let followerId = follower.id;
            let followerUrl = `${followerId}/inbox`;
            await axios.post(followerUrl, postResponse.data,
                {headers: { Authorization: getBasicHeaderValue() },});
        });

    } catch (error) {
        console.error("Failed to share post to followers:", error);
    }
}

// After posting to current author's posts, share to public inbox
// Used in CreatePost
export async function postPublicInbox(authorId, postResponse) {
    try {
        let response = await axios.get(`/api/authors/${authorId}/followers`);

        if (response.status !== 200) {
            throw new Error("Network response was not ok");
        }
        
        const data = response.data;
        for (const author of data.items){
            const id = author.id.split('/').pop();

            if (id !== authorId) {
                await axios.post(`/api/authors/${id}/inbox`, postResponse.data, {
                    headers: { 'Content-Type': 'application/json' }
                });
            }
        }
    } catch (error) {
        console.error("Failed to send post to inbox:", error);
    }
    
}


export async function postFriendsInbox(authorId, postResponse){
    try{
        let response = await axios.get(`/api/ext/authors/${authorId}/friends`)
        if (response.status !== 200) {
            throw new Error('Network response was not ok');
        }
        
        const data = response.data
        for (const author of data.items){
            const id = author.id.split('/').pop();

            if (id !== authorId) {
                await axios.post(`/api/authors/${id}/inbox`, postResponse.data, {
                    headers: { 'Content-Type': 'application/json' }
                });
            }
        } 

    } catch (error){
        console.error('Failed to send post to friends notification', error)
    }
}