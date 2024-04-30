import * as React from "react";
import {useContext, useEffect, useState} from "react";
import {
    AppBar,
    Avatar,
    Backdrop,
    Box,
    Button,
    Container,
    Divider,
    IconButton,
    List,
    ListItem,
    ListItemButton,
    Menu,
    Toolbar,
    Tooltip,
    Typography,
    useTheme,
} from "@mui/material";
import ApiIcon from "@mui/icons-material/Api";
import LogoutIcon from "@mui/icons-material/Logout";
import CreateIcon from "@mui/icons-material/Create";
import {Link} from "react-router-dom";
import SearchBar from "./SearchBar";
import {getUser} from "../../lib/User";
import Notifications from "./Notifications";
import CreatePost from "../create/CreatePost.jsx";
import {AltThemeContext} from "../../index";
import {DarkMode, LightMode} from "@mui/icons-material";
import {alpha} from "@mui/material/styles";


export default function TopBar() {
    const [user, setUser] = useState(getUser());
    const theme = useTheme();
    const {useAltTheme, setUseAltTheme} = useContext(AltThemeContext);

    useEffect(() => {
        console.log(localStorage.getItem("profileImage"));
        const handleStorageChange = () => {
            // Check if localStorage item 'profileImage' has changed
            if (localStorage.getItem("profileImage") !== user.profileImage) {
                setUser({ ...user, profileImage: localStorage.getItem("profileImage") });
            }
        };

        // Add event listener to localStorage change
        window.addEventListener("storage", handleStorageChange);

        return () => {
            // Clean up event listener
            window.removeEventListener("storage", handleStorageChange);
        };
    }, [user]);

    // PROFILE ICON ANCHOR MENU
    const [anchorElUser, setAnchorElUser] = React.useState(null);
    const handleOpenUserMenu = (event) => {
        setAnchorElUser(event.currentTarget);
    };
    const handleCloseUserMenu = () => {
        setAnchorElUser(null);
    };

    // Backdrop
    const [open, setOpen] = React.useState(false);
    const handleCreateClose = () => {
        setOpen(false);
    };
    const handleCreateOpen = () => {
        setOpen(true);
    };
    return (<AppBar position="sticky" sx={{background: theme.palette.primary.main, boxShadow: "none", zIndex: 1000}}>
            <Container maxWidth="xl">
                <Toolbar disableGutters>
                    {/* LEFT SIDE */}
                    <Box sx={{display: "flex", alignItems: "center"}}>
                        <Button component={Link} to="" disableRipple>
                            <ApiIcon sx={{
                                display: {xs: "none", md: "flex"},
                                mr: 1,
                                color: alpha(theme.palette.primary.contrastText, 0.6),
                            }}/>
                            <Tooltip followCursor title={"Navigate to home page"}>
                                <Typography
                                    variant="h6" noWrap
                                    sx={{
                                        mr: 2,
                                        display: {xs: "none", md: "flex"},
                                        fontWeight: 700,
                                        letterSpacing: ".2rem",
                                        color: alpha(theme.palette.primary.contrastText, 0.6),
                                        textDecoration: "none",
                                    }}>
                                    AUTHCORD
                                </Typography>
                            </Tooltip>
                        </Button>
                    </Box>

                    {/* SEARCH BAR */}
                    <Box sx={{flexGrow: 1, display: "flex", justifyContent: "center"}}>
                        <SearchBar/>
                    </Box>


                    {/* RIGHT SIDE */}
                    <Box sx={{flexGrow: 0, display: "flex", gap: 2}}>
                        {/* CREATE */}
                        <Tooltip followCursor title={"Create post"}>
                            <IconButton onClick={handleCreateOpen}>
                                <CreateIcon
                                    sx={{scale: "140%", color: alpha(theme.palette.primary.contrastText, 0.6)}}/>
                            </IconButton>
                        </Tooltip>

                        {/* NOTIFICATIONS */}
                        <Notifications/>

                        {/*store in storage*/}
                        <Tooltip followCursor title={`Switch to ${useAltTheme ? "light" : "dark"} theme`}>
                            <IconButton onClick={() => setUseAltTheme(!useAltTheme)}>
                                {useAltTheme
                                    ? <LightMode sx={{color: alpha(theme.palette.primary.contrastText, 0.6)}}/>
                                    : <DarkMode sx={{color: alpha(theme.palette.primary.contrastText, 0.6)}}/>}
                            </IconButton>
                        </Tooltip>

                        {/* PROFILE */}
                        <Tooltip followCursor title={"You!"}>
                            <IconButton onClick={handleOpenUserMenu} sx={{p: 0}}>
                                <Avatar src={user.profileImage} sx={{
                                    bgcolor: alpha(theme.palette.primary.contrastText, 0.6),
                                    color: theme.palette.primary.main,
                                }}/>
                            </IconButton>
                        </Tooltip>

                        {/* Menu after clicking on profile */}
                        <Menu
                            sx={{mt: "45px"}}
                            id="user-menu-appbar"
                            anchorEl={anchorElUser}
                            anchorOrigin={{
                                vertical: "top", horizontal: "right",
                            }}
                            open={Boolean(anchorElUser)}
                            onClose={handleCloseUserMenu}
                        >
                            <List sx={{width: "250px", p: 0}}>
                                <ListItem sx={{p: 0}}>
                                    <ListItemButton component={Link} to={`/profile/${user.id}`}
                                                    sx={{p: 2, height: "80%", mt: -1}}>
                                        <Box sx={{
                                            display: "flex",
                                            flexDirection: "row",
                                            alignItems: "center",
                                            gap: 1.5,
                                        }}>
                                            <Avatar src={user.profileImage}/>
                                            <Typography noWrap sx={{
                                                maxWidth: "160px",
                                                fontWeight: 600,
                                            }}>{user.username}</Typography>
                                        </Box>
                                    </ListItemButton>
                                </ListItem>
                                <Divider/>
                                <ListItem sx={{p: 0, mb: -1, background: theme.palette.secondary.main}}>
                                    <ListItemButton component={Link} to ="/sign_in" onClick={() => {
                                        localStorage.clear();
                                        window.location.reload();
                                    }}>
                                        <Box sx={{
                                            display: "flex",
                                            flexDirection: "row",
                                            alignItems: "center",
                                            color: alpha(theme.palette.secondary.contrastText, 0.6),
                                            fontWeight: 600,
                                        }}>
                                            <LogoutIcon sx={{ml: 1, mr: 2.5}}/>
                                            Sign Out
                                        </Box>
                                    </ListItemButton>
                                </ListItem>
                            </List>
                        </Menu>
                    </Box>

                </Toolbar>
            </Container>
            <Backdrop
                sx={{color: theme.palette.background.default, zIndex: (theme) => theme.zIndex.drawer + 1}}
                open={open}>
                <CreatePost handleCreateClose={handleCreateClose}/>
            </Backdrop>
        </AppBar>);
}