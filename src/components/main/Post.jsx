import React, { useState } from "react";
import {
    Backdrop, Box, Button, Container, darken, FormControl, IconButton, InputLabel, MenuItem, Select, TextField, Toolbar, Typography, useTheme
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import {fetchLocalWithBasic} from "../../lib/Url";
import {postData, shareToFollowers} from "../../lib/Posts";
import {getUser} from "../../lib/User";
import PostTemplate from "./PostTemplate";

function RegularPostInnards({post, onEdit, editable = false, deletable = editable, onProfile = false, handleEditOpen} ) {

    // not ideal
    const share = () => {
        const formData = new FormData();
        formData.append("title", post.title + " (shared from " + post.author.displayName + ")");
        formData.append("description", post.description);
        formData.append("contentType", post.contentType);
        formData.append("content", post.content);
        formData.append("visibility", post.visibility);

        postData(getUser().id, formData)
            .then(shareToFollowers)
            .then(() => window.location.reload());
    };
    const remove = () => {
        const idParts = post.id.split("/");
        const authorId = idParts[idParts.length - 3];
        const postIdPart = idParts[idParts.length - 1];
        const deleteUrl = `/authors/${authorId}/posts/${postIdPart}`;

        try {
            fetchLocalWithBasic(deleteUrl, {method: "DELETE"})
                .then(() => console.log("Deleted post!"))
                .then(() => window.location.refresh()); // BAD
        } catch (error) {
            console.error("Error deleting post:", error);
        }
    };
    return (
        <PostTemplate onProfile={onProfile} post={post} share={share} remove={remove} editable={editable}
                      onEdit={onEdit} handleEditOpen={handleEditOpen}/>
    );
}

/**
 *
 * @param {Object} post
 * @param onClose
 * @returns {Element}
 * @constructor
 */
function EditPostInnards({post, onClose, handleEditClose}) {
    const theme = useTheme();

    const [modifiedPost, setModifiedPost] = useState(post);

    const handleEditChange = (keyName) => (event) => {
        setModifiedPost({...modifiedPost, [keyName]: event.target.value});
    };

    const [saved, setSaved] = useState(false);

    const saveAlert = (success) => {
        if (success) {
            console.log("Saved edits successfully!");
        } else {
            console.log("Failed to save edits!");
        }
    };

    const handleSave = () => {
        const authorId = post.author.id.split("/").pop();
        const postId = post.id.split("/").pop(); // Extract postId from post URL

        const data = Object.keys(modifiedPost).reduce((acc, key) => {
            if (modifiedPost[key] !== post[key]) {
                acc[key] = modifiedPost[key];
            }
            return acc;
        }, {});
        // TODO give feedback, close on error
        // TODO update client side content as well
        fetchLocalWithBasic(`/authors/${authorId}/posts/${postId}`, {
            method: "PUT", body: JSON.stringify(data), headers: {"Content-Type": "application/json"},
        })
            .then(r => {
                setSaved(r.ok);
                return r.ok;
            })
            .then(saveAlert)
            .then(onClose);
    };

    return (
        <Container sx={{display:'flex', flexDirection:'column', alignItems:'center', width:'50%', maxHeight:'100%', my:1}}>
                <Box sx={{
                display:'flex', 
                flexDirection:'row', 
                alignItems:'center', 
                justifyContent:'space-between',
                width:'100%', 
                height:'50px',
                color: theme.palette.secondary.contrastText,
                background: theme.palette.secondary.main,
                p:1,
                borderTopLeftRadius:'10px',
                borderTopRightRadius:'10px',
                }}>
                    <IconButton onClick={handleEditClose}>
                        <ArrowBackIcon sx={{color: theme.palette.secondary.contrastText}}/>
                    </IconButton>
                    <Typography variant="h6">Edit post</Typography>
                    <Toolbar/>
                </Box>

                <Container sx={{display:'flex', flexDirection:'column', alignItems:'center', width:'100%', background:theme.palette.background.default}}>
                    <TextField 
                        fullWidth
                        label="Title"
                        variant="outlined"
                        value={modifiedPost.title}
                        onChange={handleEditChange("title")}
                        sx={{my: 2}}
                    />

                    <TextField
                        fullWidth
                        label="Description"
                        variant="outlined"
                        value={modifiedPost.description}
                        onChange={handleEditChange("description")}
                        sx={{mb: 2}}
                    />

                    <TextField
                        fullWidth
                        label="Content"
                        variant="outlined"
                        multiline
                        rows={6}
                        value={modifiedPost.content}
                        onChange={handleEditChange("content")}
                        sx={{mb: 2}}
                    />

                    <FormControl fullWidth sx={{mb: 2}}>
                        <InputLabel>Content Type</InputLabel>
                        <Select
                            value={modifiedPost.contentType}
                            label="Content Type"
                            onChange={handleEditChange("contentType")}
                        >
                            <MenuItem value="text/plain">Plain Text</MenuItem>
                            <MenuItem value="text/markdown">Markdown</MenuItem>
                            <MenuItem value="image/png;base64">PNG (Base64)</MenuItem>
                            <MenuItem value="image/jpeg;base64">JPEG (Base64)</MenuItem>
                        </Select>
                    </FormControl>

                    <FormControl fullWidth sx={{mb: 2}}>
                        <InputLabel>Visibility</InputLabel>
                        <Select
                            value={modifiedPost.visibility}
                            label="Visibility"
                            onChange={handleEditChange("visibility")}
                        >
                            <MenuItem value="PUBLIC">Public</MenuItem>
                            <MenuItem value="FRIENDS">Friends</MenuItem>
                            <MenuItem value="PRIVATE">Private</MenuItem>
                        </Select>
                    </FormControl>

                    <Button fullWidth onClick={handleSave} variant="contained" sx={{
                    height: "25px",
                    borderRadius: "10px",
                    mb:2,
                    color: theme.palette.primary.contrastText,
                    background: theme.palette.primary.main,
                    "&:hover": {
                        background: darken(theme.palette.primary.main, 0.2),
                    },
                    }}>
                        <Typography sx={{ml:-2}}>Save</Typography>
                    </Button>

                </Container>

        </Container>

    );
}

export default function Post({post, editable = false, onProfile = false}) {
    const [editMode, setEditMode] = useState(false);
    const theme = useTheme();
    // Backdrop
    const [open, setOpen] = React.useState(false);
    const handleEditClose = () => {
        setOpen(false);
        window.location.reload();   // post doesn't appear after exiting edit unless reload for some reason
    };
    const handleEditOpen = () => {
        setOpen(true);
    };

    return (
        <Container sx={{ display: "flex", flexDirection: "column", width: "100%", alignItems:'center' }}>
            {(editable && editMode) ? (
                <Backdrop sx={{color: theme.palette.background.default, zIndex: (theme) => theme.zIndex.drawer + 1}}
                open={open}>
                    <EditPostInnards post={post} onClose={() => {setEditMode(false);}} handleEditClose={handleEditClose}/>
                </Backdrop>
            ) :
                <RegularPostInnards onProfile={onProfile} editable={editable} post={post} onEdit={() => setEditMode(true)} handleEditOpen={handleEditOpen}/>}
        </Container>
    );
}
