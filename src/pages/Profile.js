import React, {useEffect, useMemo, useState} from "react";
import {Avatar, Backdrop, Box, Button, Card, Container, CircularProgress, darken, LinearProgress, Pagination, TextField, Typography, IconButton, Toolbar} from "@mui/material";
import GitHubIcon from '@mui/icons-material/GitHub';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import {useParams} from "react-router-dom";
import Divider from "@mui/material/Divider";
import {getUser, setUser, getBasicHeaderValue} from "../lib/User";
import {fetchLocal, fetchLocalWithBasic} from "../lib/Url";
import {foreignFollowDelete, foreignFollowGet, inboxPost} from "../lib/API";
import {ceil, isEmpty} from "lodash";
import Post from "../components/main/Post";
import { theme } from "../theme";
import axios from 'axios';

async function getAuthorDetails(id) {
    return await fetchLocal(`/authors/${id}/`).then(u => u.json());
}

async function triggerGithubActivity(authorId) {
    try {
        const profileResponse = await fetchLocalWithBasic(`/authors/${authorId}/`).then(u => u.json());
        const name = profileResponse.github.split("/").pop();
        if (name !== "") {
            try {
                const response = await fetchLocalWithBasic(`/ext/authors/${authorId}/github_activity`);
                if (response.ok) {
                    console.log("Fetched GitHub activity");
                }
            } catch (error) {
                console.error("Failed to fetch GitHub activity:", error);
            }
        }
    } catch (error) {
        console.error("Failed to fetch profile data:", error);
    }
}


function ProfileHeader({user}) {
    // PROFILE IMAGE
    const changeProfileImage= async () => {
    
        const authorId = getUser().id;
        const profileImage = document.getElementById('profilePictureURL').value;
        const authorDetailsUrl = `/api/authors/${authorId}/`;
        try{
            //set user with updated profileImage to update top bar avatar
            setUser({
                ...getUser(),
                profileImage: profileImage
            });

            let response = await axios.put(authorDetailsUrl, {profileImage: profileImage}, {
                headers: { Authorization: getBasicHeaderValue() },
            });
            return response
            
        } catch (error) {
            console.error('Failed to upload profile image:', error);
            return null;
        }
    }

    // GITHUB
    const gitHubState = useState(user.github?.split("/").pop());
    /** @type string */
    const gitHubUsername = gitHubState[0];
    const setGitHubUsername = gitHubState[1];
    const rawId = user.id.split("/").pop();
    const handleAddGitHub = async () => {
        const prefix = "https://github.com/";
        const githubUrl = prefix.concat(gitHubUsername);
        try {
            await fetchLocalWithBasic(`/authors/${rawId}/`, {
                method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify({github: githubUrl}),
            });
        } catch (error) {
            console.error("Failed to add GitHub:", error);
        }
    };

    // Backdrop
    const [open, setOpen] = React.useState(false);
    const handleEditProfileClose = () => {
      setOpen(false);
      window.location.reload();
    };
    const handleEditProfileOpen = () => {
      setOpen(true);
    };


    // SELF PROFILE
    return (
        <Container sx={{display:'flex', flexDirection:'column', alignItems:'center', width:'100%'}}>
            <Avatar
                alt="Profile Picture"
                src={user.profileImage}
                sx={{width: 120, height: 120, mt:2, mb:1}}
            />
            <Typography variant="h4" sx={{mt: 1}}>{user.displayName}</Typography>
            {user.github && (
                <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', my:1}}>
                    <GitHubIcon sx={{mr: .5}}/>
                    <Typography variant="body2" color="text.secondary" component="a" href={user.github} target="_blank" rel="noopener noreferrer" sx={{ textDecoration: 'none' }}>
                        {gitHubUsername}
                    </Typography>
                </Box>
            )}
            <Button variant="contained" sx={{background:theme.palette.primary.main, color: "black", borderRadius: "10px", fontSize: "0.7rem"}} onClick={handleEditProfileOpen}> Edit Profile</Button>
            <Divider sx={{color:'black', width:'60%', height:0.5, my:2}}/>
            <Backdrop
                sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1}} open={open}>
                    <Container sx={{display:'flex', flexDirection:'column', width:'400px'}}>
                        <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', width:'100%', height:'40px', justifyContent:'space-between', color:'white', background:theme.palette.secondary.main, borderTopLeftRadius:'10px', borderTopRightRadius:'10px'}}>
                            <IconButton onClick={handleEditProfileClose}><ArrowBackIcon sx={{color:theme.palette.secondary.contrastText}}/></IconButton>
                            <Typography variant="h6">Edit Profile</Typography>
                            <Toolbar/>
                        </Box>

                        <Card variant="outlined" sx={{display:'flex', flexDirection:'column', alignItems:'start', p:1}}>
                            
                            <Typography sx={{color:'black'}}>Change Github</Typography>
                            <Box sx={{display:'flex', flexDirection:'row', alignItems:'center'}}>
                                <TextField
                                    size="medium"
                                    variant="outlined"
                                    placeholder="Enter GitHub username"
                                    value={gitHubUsername ?? ""}
                                    onChange={(e) => setGitHubUsername(e.target.value)}
                                    sx={{mr: 1,
                                        "& .MuiOutlinedInput-root": {
                                            borderRadius: "10px",
                                        }
                                    }}
                                />
                                <Button variant="contained" onClick={handleAddGitHub} sx={{
                                    width:"100px",
                                    height: "25px",
                                    borderRadius:"10px",
                                    color: theme.palette.primary.contrastText,
                                    background: theme.palette.primary.main,
                                    "&:hover": {
                                        background: darken(theme.palette.primary.main, 0.2),
                                    },
                                }}> 
                                    Submit
                                </Button>
                            </Box>
                        </Card>

                        <Card variant="outlined" sx={{display:'flex', flexDirection:'column', alignItems:'start', p:1}}>
                            <Typography sx={{color:'black'}}>Change Profile Image</Typography>
                            <Box sx={{display:'flex', flexDirection:'row', alignItems:'center'}}>
                                <TextField
                                    id="profilePictureURL"
                                    size="small"
                                    variant="outlined"
                                    placeholder="Enter Image URL"
                                    sx={{mr: 1,
                                        "& .MuiOutlinedInput-root": {
                                            borderRadius: "10px",
                                        }
                                    }}
                                />
                                <Button variant="contained" onClick={changeProfileImage} sx={{
                                    width:"100px",
                                    height: "25px",
                                    borderRadius:"10px",
                                    color: theme.palette.primary.contrastText,
                                    background: theme.palette.primary.main,
                                    "&:hover": {
                                        background: darken(theme.palette.primary.main, 0.2),
                                    },
                                }}> 
                                    Submit
                                </Button>
                            </Box>
                        </Card>

                    </Container>
            </Backdrop>
        </Container>
    );
}


function Posts({authorId, user, editable = false}) {
    const [page, setPage] = useState(1);
    const [postCount, setPostCount] = useState(undefined);
    const pageSize = 10;
    const pageCount = useMemo(() => ceil(postCount / pageSize), [postCount]);
    const [posts, setPosts] = useState(undefined);

    useEffect(() => {
        fetchLocalWithBasic(`/authors/${authorId}/posts/?page=${page}&size=${pageSize}`)
            .then(r => r.json())
            .then(r => setPosts(r));
    }, [authorId, page, pageCount]);

    useEffect(() => {
        fetchLocalWithBasic(`/ext/authors/${authorId}/post_count`)
            .then(r => r.json())
            .then(r => setPostCount(r.count));
    }, [authorId]);

    return (<>
        {posts !== undefined && posts.items.map(post => <Post onProfile editable={editable} post={post}/>)}
        {postCount === undefined ? <CircularProgress/> :
            <Pagination count={pageCount} page={page} onChange={(_, p) => setPage(p)} showFirstButton/>}
    </>);
}

const Profile = () => {
    // the id of the author being viewed
    const {id} = useParams();

    const [user, setUser] = useState({});
    const [loggedInUser, setLoggedInUser] = useState({});

    const [status, setStatus] = useState("Follow");

    const [currentPage] = useState(1);
    const pageSize = 10;

    const receiver_id = id.split("/").pop();

    const loggedInAuthorId = getUser().id;
    const handleRequest = () => {
        if (status === "Follow") {
            let postData = {
                summary: `${getUser().username} wants to follow ${user.displayName}`,
                type: "Follow",
                actor: loggedInUser,
                object: user,
            };
            inboxPost(postData, id)
                .then(() => console.log("Successfully sent follow to inbox."));
        } else if (status === "Following") {
            foreignFollowDelete(receiver_id, `${getUser().serverName}/api/authors/${getUser().id}`)
                .then(r => {
                    if (r.ok) {
                        setStatus("Follow");
                    } else {
                        console.log("Error: failed to unfollow");
                    }
                });
        }
    };

    useEffect(() => {
        // Immediately-invoked async function for handling async logic
        (async () => {
            try {
                const loggedUserDetails = await getAuthorDetails(loggedInAuthorId);
                setLoggedInUser(loggedUserDetails);

                if (receiver_id === loggedInAuthorId) {
                    await triggerGithubActivity(receiver_id);
                } else {
                    const receiverUserDetails = await getAuthorDetails(receiver_id);
                    setUser(receiverUserDetails);

                    try {
                        const followStatus = await foreignFollowGet(id, loggedUserDetails.id);
                        setStatus(followStatus.ok ? "Following" : "Follow");
                    } catch (error) {
                        console.error("Error checking request status:", error);
                    }
                }
            } catch (error) {
                console.error("Error in useEffect:", error);
            }
        })();
    }, [currentPage, pageSize, loggedInAuthorId, receiver_id, id]);

    // SELF PROFILE
    if (id === loggedInAuthorId) {
        return (<Container sx={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            width: "100%",
            maxWidth: "400px",
        }}>
            {isEmpty(loggedInUser) ? <CircularProgress/> : <ProfileHeader user={loggedInUser}/>}
            {isEmpty(loggedInUser) ? <LinearProgress/> : <Posts editable user={loggedInUser} authorId={id}/>}
        </Container>);
    } else { 
        // OTHER PROFILE, duplicated from self profile except for edit profile button --> follow status
        return (
            <Container sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                width: "100%",
            }}>
                <Avatar
                    alt="Profile Picture"
                    src={user.profileImage}
                    sx={{width: 120, height:120, mt:2, mb:1}}
                />
                <Typography variant="h4" sx={{mt: 1}}>{user.displayName}</Typography>
                {user.github && (
                    <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', my:1}}>
                        <GitHubIcon sx={{mr: .5}}/>
                        <Typography variant="body2" color="text.secondary" component="a" href={user.github} target="_blank" rel="noopener noreferrer" sx={{ textDecoration: 'none' }}>
                            {user.github.split("/").pop()}
                        </Typography>
                    </Box>
                )}
                <Button variant="contained" sx={{background:theme.palette.primary.main, color: "black", borderRadius: "10px", fontSize: "0.7rem"}}
                        onClick={handleRequest}> {status} </Button>
                <Divider sx={{color:'black', width:'60%', height:0.5, my:2}}/>
                {isEmpty(user) ? <CircularProgress/> : <Posts user={user} authorId={id}/>}
            </Container>
        );
    }

};
export default Profile;
