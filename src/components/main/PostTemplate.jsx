import {Avatar, Box, Card, Container, Divider, IconButton, Menu, MenuItem, Tooltip, Typography} from "@mui/material";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import GroupsIcon from "@mui/icons-material/Groups";
import GroupIcon from "@mui/icons-material/Group";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import ShareIcon from "@mui/icons-material/Share";
import CommentIcon from "@mui/icons-material/Comment";
import React, {useMemo, useState} from "react";
import {Link} from "react-router-dom";
import ReactMarkdown from "react-markdown";
import LikeButton from "./LIkeButton";

const PostTemplate = ({post, share, remove, editable, onEdit, onProfile = false, handleEditOpen}) => {
    const [anchorEl, setAnchorEl] = useState(null);

    const handleMenuOpen = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };


    const imageScheme = useMemo(() => {
        if (post.content.startsWith("data:")) {
            return null;
        } else {
            return `data:${post.contentType}`;
        }
    }, [post])

    return (
        <Container sx={{display:'flex', flexDirection:'column', alignItems:'center', width:'600px', maxHeight:'640px', my:1}}>
            <Card variant="outlined" sx={{width:'100%', height:'100%', borderRadius:'10px'}}>
            {/* Header */}
            <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', justifyContent:'space-between'}}>
                <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', m:2}}>
                    {/* TODO: LINK author id has no dashes */}
                    <Avatar component={Link} to={`/profile/${post.author.id.split('/').pop()}`} src={post.author.profileImage}/>
                    <Typography component={Link} to={`/profile/${post.author.id.split('/').pop()}`} sx={{ml:1, fontWeight:600, textDecoration:'none', color:'inherit'}}>{post.author.displayName}</Typography>
                </Box>

                <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', mr:1}}>
                    <Card variant="outlined" sx={{
                        display: "flex",
                        flexDirection: "row",
                        alignItems: "center",
                        p: 0.5,
                        borderRadius: "10px",
                    }}>
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

                    {editable &&
                        <Tooltip followCursor title={"More options"}>
                            <IconButton onClick={handleMenuOpen}>
                                <MoreVertIcon/>
                            </IconButton>
                        </Tooltip>
                    }
                    <Menu
                        anchorEl={anchorEl}
                        open={Boolean(anchorEl)}
                        onClose={handleMenuClose}
                    >
                        <MenuItem onClick={() => { handleEditOpen(); onEdit(); handleMenuClose(); }}>Edit</MenuItem>
                        <MenuItem onClick={() => { remove(); handleMenuClose(); }} sx={{color:'red', fontWeight:600}}>Delete</MenuItem>
                    </Menu>
                </Box>
            </Box>

            {/* Title Description */}
            <Box sx={{ display: 'flex', flexDirection: 'column',alignItems: 'start', ml: 4, mt: -1, maxWidth:'500px' }}>
                    <Typography 
                    variant="h6" 
                    component={Link} 
                    to={`/authors/${post.author.id.split('/').pop()}/posts/${post.id.split('/').pop()}`}
                    sx={{ overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 1, WebkitBoxOrient: 'vertical', textAlign:'start', maxWidth:'500px', textDecoration:'none', color:'inherit' }}>
                        {post.title}
                    </Typography>
                <Typography variant="caption" sx={{ overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', maxWidth: '90%', textAlign:'start' }}>{post.description}</Typography>
            </Box>

            <Divider sx={{my:1}}/>
            
            <Box 
            component={Link} 
            to={`/authors/${post.author.id.split('/').pop()}/posts/${post.id.split('/').pop()}`}
            sx={{display:'flex', flexDirection:'column', alignItems:'start', ml: 4, width:'100%', maxHeight:'30vh', textDecoration:'none', color:'inherit', overflow:'hidden'}}>

                {post.contentType === "text/plain" ? (
                    <Typography sx={{overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth:'500px'}}>
                        {post.content}
                    </Typography>) : 
                post.contentType.startsWith("image/") ? (
                    <img
                        src={`${imageScheme !== null ? imageScheme + "," : ""}${post.content}`}
                    alt="Post"
                    sx={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                    />
                    ) : (
                        <Box sx={{maxWidth:'480px', overflow:'hidden', whiteSpace:'nowrap'}}>
                            <ReactMarkdown>{post.content}</ReactMarkdown>
                        </Box>
                 )}
            </Box>

            <Divider sx={{my:1, width:'100%'}}/>
            <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', ml: 3, mb:1, gap:1}}>
                {!onProfile && <>
                    <LikeButton objectUrl={post.id} type="post"/>
                    <Tooltip followCursor title={"Expand post and view comments."}>
                        <IconButton component={Link}
                                    to={`/authors/${post.author.id.split("/").pop()}/posts/${post.id.split("/").pop()}`}>
                            <CommentIcon/>
                        </IconButton>
                    </Tooltip>
                <Tooltip followCursor title={"Share this post."}>
                    <IconButton onClick={share}>
                        <ShareIcon/>
                    </IconButton>
                </Tooltip>
                </>
                } 
            </Box>
            </Card>

        </Container>
    )
}

export default PostTemplate