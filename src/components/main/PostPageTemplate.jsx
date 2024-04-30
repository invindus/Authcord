
import {
    Avatar,
    Box,
    Button,
    Card,
    CircularProgress,
    Container,
    darken,
    Divider,
    IconButton,
    TextField,
    Toolbar,
    Tooltip,
    Typography,
} from "@mui/material";
import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom';
import GroupsIcon from '@mui/icons-material/Groups';
import GroupIcon from '@mui/icons-material/Group';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import ShareIcon from '@mui/icons-material/Share';
import LikeButton from './LIkeButton';
import ReactMarkdown from "react-markdown";
import { getUser } from '../../lib/User';
import { shareToFollowers, postData } from '../../lib/Posts';
import Comment from './Comment';
import { postComment } from '../../lib/Comments';
import { fetchLocalWithBasic } from '../../lib/Url';
import { theme } from '../../theme';

function PostComments({postId}) {
    const [comments, setComments] = useState(undefined);
    const [writtenComment, setWrittenComment] = useState("");
    const idParts = postId.split("/");
    const authorId = idParts[idParts.length - 3];
    const postIdPart = idParts[idParts.length - 1];
    const commentBaseUrl = `/authors/${authorId}/posts/${postIdPart}/comments`;
  
    const submit = () => {
        postComment(writtenComment, `/api${commentBaseUrl}`)
            .then(() => {
                setWrittenComment("");
            }).then(_ => window.location.reload()); // BAD
    };
  
    useEffect(() => {
        fetchLocalWithBasic(`${commentBaseUrl}?page=1&size=255`)
            .then(r => r.json())
            .then(r => setComments(r));
    }, [commentBaseUrl]);
  
    return (<>
        <Box sx={{display:'flex', flexDirection:'column', alignItems:'center', width:'100%'}}>
            <TextField
                fullWidth rows={2}
                label="Write a comment..."
                variant="outlined"
                value={writtenComment}
                onChange={e => setWrittenComment(e.target.value)}
                inputProps={{ maxLength: 40}}
                sx={{my: 1}}
            />
            <Box sx={{display:'flex', flexDirection:'column', alignItems:'end', width:'100%'}}>
                <Button variant="contained" onClick={() => {submit()}} sx={{
                    width: "120px",
                    height: "25px",
                    borderRadius: "10px",
                    mt:-5,
                    mr:1,
                    color: theme.palette.primary.contrastText,
                    background: theme.palette.primary.main,
                    "&:hover": {
                        background: darken(theme.palette.primary.main, 0.2),
                    },
                }}>Post</Button>
            </Box>
        </Box>
        <Box sx={{display:'flex', flexDirection:'column', width:'100%', alignItems:'start'}}>
            {comments === undefined ? <CircularProgress/> : comments.comments.map(comment => <Comment comment={comment}/>)}
        </Box>
    </>);
  }

const PostPageTemplate = ({ post }) => {

    // from Post.jsx, except doesn't reload window
    const share = () => {
        const formData = new FormData();
        formData.append("title", post.title + " (shared from " + post.author.displayName + ")");
        formData.append("description", post.description);
        formData.append("contentType", post.contentType);
        formData.append("content", post.content);
        formData.append("visibility", post.visibility);

        postData(getUser().id, formData)
            .then(shareToFollowers)
    };

    return(
        <Container sx={{width:"70vw", height:'90vh', display: "flex", flexDirection: "row", alignItems:"center"}}>
                {/* CONTENT */}
                <Card variant="outlined" sx={{display:'flex', width:'100%', height:'100%', alignItems: 'center', justifyContent: 'center'}}>
                    {post.contentType === "text/plain" ? (
                        <Typography sx={{ textAlign:'start', overflowWrap: 'break-word', maxWidth: '100%', p:2 }}>
                            {post.content}
                        </Typography>) : 
                    post.contentType.startsWith("image/") ? (
                        <img 
                        src={`data:${post.contentType};base64,${post.content}`} 
                        alt="Post"
                        style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', p:2 }}/>) : (
                        <Box sx={{ textAlign: 'start', overflowWrap: 'break-word', maxWidth: '100%', p: 2 }}>
                            <ReactMarkdown>{post.content}</ReactMarkdown>
                        </Box>
                    )}
                </Card>

                <Card variant="outlined" sx={{display:'flex', flexDirection:'column', alignItems:'center', width:'100%', height:'100%'}}>
                    <Box sx={{display:'flex', flexDirection:'row', width:'100%', alignItems:'center', justifyContent:'space-between'}}>
                        <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', m:2}}>
                            {/* TODO: LINK author id has no dashes */}
                            {/* AVATAR + USERNAME */}
                            <Avatar component={Link} to={`/profile/${post.author.id.split('/').pop()}`} src={post.author.profileImage}/>
                            <Typography component={Link} to={`/profile/${post.author.id.split('/').pop()}`} sx={{ml:1, fontWeight:600, textDecoration:'none', color:'inherit'}}>{post.author.displayName}</Typography>
                        </Box>

                        <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', mr:1}}>
                        
                            {/* VISIBILITY + DATE */}
                            <Card variant="outlined" sx={{display:'flex', flexDirection:'row', alignItems:'center', p:0.5, borderRadius:'10px'}}>
                                {post.visibility === "PUBLIC" ? <Tooltip followCursor title={"Public"}>
                                    <GroupsIcon sx={{mr: 1}}/>
                                </Tooltip> : post.visibility === "FRIENDS" ? <Tooltip followCursor title={"Friends only"}>
                                    <GroupIcon sx={{mr: 1}}/>
                                </Tooltip> : post.visibility === "UNLISTED" && <Tooltip followCursor title={"Unlisted"}>
                                    <VisibilityOffIcon sx={{mr: 1}}/>
                                </Tooltip>}

                                <Tooltip followCursor title={"Publish date"}>
                                    <Typography variant="caption">{new Date(post.published).toLocaleDateString()}</Typography>
                                </Tooltip>
                            </Card>
                        </Box>
                    </Box>

                    <Divider sx={{my:1, width:'100%'}}/>
                    
                    {/* TITLE + DESC */}
                    <Box sx={{display:'flex', flexDirection:'column', width:'100%', alignItems:'start'}}>
                        <Box sx={{display:'flex', flexDirection:'column', alignItems:'start', width:'92%', maxHeight:'120px', ml:2}}>
                            <Typography variant="h5" sx={{maxWidth:'100%', overflow:'auto'}}>{post.title}</Typography>
                            <Typography sx={{mt:1, maxWidth:'100%', overflow:'auto'}}>{post.description}</Typography>
                        </Box>

                        {/* LIKE + SHARE */}
                        <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', gap:1, ml:1}}>
                            <LikeButton objectUrl={post.id} type="post"/>
                            <Tooltip followCursor title={"Share this post."}>
                                <IconButton onClick={share}>
                                    <ShareIcon/>
                                </IconButton>
                            </Tooltip>
                        </Box>
                    </Box>

                    <PostComments postId={post.id}/>
                </Card>


        </Container>
    )
}

export default PostPageTemplate