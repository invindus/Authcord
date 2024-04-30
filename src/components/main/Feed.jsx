import React, {useEffect, useMemo, useState} from "react";
import {Box, Container, CircularProgress, Pagination} from "@mui/material";
import {getPosts} from "../../lib/Posts";
import Post from "./Post";
import {ceil} from "lodash";
import {fetchLocalWithBasic} from "../../lib/Url";

export default function Feed() {
    const [page, setPage] = useState(1);
    const [postCount, setPostCount] = useState(undefined);
    const pageSize = 5;
    const pageCount = useMemo(() => ceil(postCount / pageSize), [postCount]);
    const [posts, setPosts] = useState(undefined);

    useEffect(() => {
        getPosts(page, pageSize)
            .then(posts => setPosts(posts)); 
    }, [page]);

    useEffect(() => {
        fetchLocalWithBasic("/ext/post_count")
            .then(r => r.json())
            .then(r => setPostCount(r.count));
    }, []);

    return (
        <Container className="feed" sx={{width:"100%", display: "flex", flexDirection: "column", alignItems:"center"}}>
            {posts !== undefined && posts.items.map(post => <Post post={post}/>)}
            {postCount === undefined ? <CircularProgress/> :
                <Pagination count={pageCount} page={page} onChange={(_, p) => setPage(p)} showFirstButton/>}
        </Container>
    );
}