import React from 'react'
import { Avatar, Box, Typography } from '@mui/material'

const Notification = ( { notif } ) => {
  return (
    <Box className='notification' sx={{display: 'flex', justifyContent:'space-between', padding: '5px'}}>
        <Box style={{display: 'flex', alignItems: 'center'}}>
            <Avatar sx={{ml:'14px', mr: 1}} src={notif.author.profileImage}/>
            <Typography sx={{textAlign: 'left', fontSize: '14px'}}> {notif.author.displayName} </Typography>
            <Typography sx={{textAlign: 'left', ml: '4px', fontSize: '14px'}}>
                {notif.type === "Like" ? "liked your post." :
                    notif.type === "comment" ? "commented on your post." :
                    notif.type === "post" ? "shared a post." : "sent a notification"
                }
            </Typography>
        </Box>


    </Box>
  )
}

export default Notification