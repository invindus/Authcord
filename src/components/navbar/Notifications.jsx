import {Box, Divider, IconButton, List, Menu, Toolbar, Tooltip, Typography, useTheme} from "@mui/material";
import React, {useState} from "react";
import NotificationsIcon from "@mui/icons-material/Notifications";
import LayersClearIcon from "@mui/icons-material/LayersClear";
import {RequireValidation} from "../RequireValidation";
import {inboxDelete, inboxGet} from "../../lib/API";
import Request from "./Request";
import Notification from "./Notification";
import {alpha} from "@mui/material/styles";

const Notifications = () => {
    const [requestNotifications, setRequestNotification] = useState([]);
    const [otherNotifications, setOtherNotification] = useState([]);

    const theme = useTheme();

    const getInbox = () => {
        setOtherNotification([])
        setRequestNotification([])
        try {
            inboxGet().then(items => {
                setRequestNotification(items.filter(item => item.type === "follow") || [])
                setOtherNotification(items.filter(item => item.type !== "follow") || [])
            })
        } catch (error) {
            console.log(error)
        }
    }

    const clearInbox = () => {
        try {
            inboxDelete()
                .then(response => {
                    if (response.ok) {
                        setRequestNotification([]);
                        setOtherNotification([]);
                        console.log("Inbox cleared successfully");
                    }
                })
        } catch (error) {
            console.log("Failed to clear inbox:", error);
        }
    };

    // NOTIFICATION ANCHOR MENU
    const [anchorElNotif, setAnchorElNotif] = React.useState(null);
    const handleOpenNotifMenu = (event) => {
        setAnchorElNotif(event.currentTarget);
        getInbox();
    };
    const handleCloseNotifMenu = () => {
        setAnchorElNotif(null);
    };
    
  return (
    <RequireValidation>
    <Box>
        <Tooltip followCursor title={"View inbox"}>
            <IconButton onClick={handleOpenNotifMenu} sx={{p: 1.2}}>
                <NotificationsIcon sx={{scale: "140%", color: alpha(theme.palette.primary.contrastText, 0.6)}}/>
            </IconButton>
        </Tooltip>

            {/* DROP DOWN LIST */}
            <Menu
            sx={{ mt: '45px'}}
            id="notif-menu-appbar"
            anchorEl={anchorElNotif}
            anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
            }}
            open={Boolean(anchorElNotif)}
            onClose={handleCloseNotifMenu}
            >
                <Box sx={{display:'flex', flexDirection:'column', width:'380px', maxHeight:'560px'}}>
                    <Box className='notifHeader' sx={{
                        position:'sticky',
                        top:0,
                        display:'flex',
                        flexDirection:'row',
                        zIndex:1000,
                        height:'40px',
                        alignItems:'center',
                        justifyContent:'space-between',
                        color: 'white',
                        background: theme.palette.secondary.main,
                        mt:-1,
                        fontWeight:600
                    }}>
                        <Toolbar/> 
                            Notifications
                        <Tooltip title={"Clear notifications"} followCursor>
                            <IconButton sx={{mr: "10px"}}>
                                <LayersClearIcon sx={{scale: "120%", color: "white"}} onClick={clearInbox}/>
                            </IconButton>
                        </Tooltip>
                    </Box>

                    <Box sx={{overflow:'hidden', flex:1}}>
                        {/* Follow Requests */}
                        <List className="requestList"sx={{ maxHeight: '200px', overflowY: 'auto', position: 'relative' }}>
                            {requestNotifications.length > 0 ? (requestNotifications.map(request => (
                                <Request key={request.id} request={request}/>))) : (
                                <Box sx={{display:'flex', justifyContent:'center', alignItems:'center', height:'100%'}}>
                                    <Typography fontSize={14}>No follow requests.</Typography>
                                </Box>
                                )
                            }
                        </List>
                    </Box>

                    <Divider sx={{ml:'14px', mr:'14px'}}/>

                    <Box sx={{overflow:'hidden', flex:1}}>
                        {/* Other Notifications */}
                        <List className="notifList" sx={{ maxHeight: '200px', overflowY: 'auto', position: 'relative' }}>
                            {otherNotifications.length > 0 ? (otherNotifications.map(notif => (
                                <Notification key={notif.id} notif={notif}/>))) : (
                                <Box sx={{display:'flex', justifyContent:'center', alignItems:'center', height:'100%'}}>
                                    <Typography fontSize={14}>No other notifications.</Typography>
                                </Box>
                                )
                            }
                        </List>
                    </Box>


                </Box>

            </Menu>
    </Box>
    </RequireValidation>

  )
}

export default Notifications