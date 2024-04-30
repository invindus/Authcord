import React, {useEffect, useState} from "react";
import {getLikes, likeSubmit} from "../../lib/Likes";
import FavoriteIcon from "@mui/icons-material/Favorite";
import {CircularProgress, IconButton, Tooltip, Typography} from "@mui/material";

export default function LikeButton({type, objectUrl, object, sx}) {
    if (objectUrl === undefined) {
        objectUrl = object.id
    }
    const likesState = useState(undefined);
    /** @type {(int | undefined)} */
    const likes = likesState[0];
    const setLikes = likesState[1];
    const [liked, setLiked] = useState(false);

    useEffect(() => {
        let likesUrl;
        if (type === "post") {
            const idParts = objectUrl.split("/");
            const authorId = idParts[idParts.length - 3];
            const postIdPart = idParts[idParts.length - 1];
            likesUrl = `/api/authors/${authorId}/posts/${postIdPart}/likes`;
        } else if (type === "comment") {
            const idParts = objectUrl.split("/");
            const authorId = idParts[idParts.length - 5];
            const postIdPart = idParts[idParts.length - 3];
            const commentId = idParts[idParts.length - 1];
            likesUrl = `/api/authors/${authorId}/posts/${postIdPart}/comments/${commentId}/likes`;
        }
        getLikes(likesUrl)
            .then(setLikes); 

    }, [type, objectUrl, setLikes]);
    
    const like = () => {
        if (!liked) {
            const urlSegments = objectUrl.split("/");

            const lastId = urlSegments[urlSegments.length - 1]; 
            const postId = type === "comment" ? urlSegments[urlSegments.length - 3] : lastId;
            const authorId = urlSegments[urlSegments.length - (type === "comment" ? 5 : 3)];

            let maybeCommentId = type === "comment" ? (object ?? objectUrl) : undefined;
            
            if (authorId && postId && (type === "post" || (type === "comment" && maybeCommentId))) {
                likeSubmit(authorId, postId, maybeCommentId)
                    .then(([likedResponse, newLikes]) => {
                        if (likedResponse) {
                            setLikes(newLikes);
                            setLiked(true);
                            console.log("Liked");
                        }
                    });
            } else {
                console.error("Error: Incorrect ID parsing from URL.");
            }
        }
    };

    return (<>{likes === undefined ? <CircularProgress sx={{mr:2}}/> :

        <Tooltip followCursor title={`Like this ${type}.`}>
            <IconButton onClick={like}>
                <FavoriteIcon sx={{mr: 1, color: liked ? "red" : undefined}}/>
                <Typography>{likes !== undefined ? likes : ""}</Typography>
            </IconButton>
        </Tooltip>
        }</>);
}
