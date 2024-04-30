import React from 'react'
import { Avatar, Box, Button, IconButton, Typography } from '@mui/material'
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import { useState } from 'react'
import {fetchLocalWithBasic} from "../../lib/Url";
import {foreignFollowPut, requestDelete} from "../../lib/API";

const Request = ( { request } ) => {

    const [requestStatus, setRequestStatus] = useState('Pending');
    const sender_url = request.actor.id;
    const sender_id = sender_url.split('/').pop();
    const receiver_url = request.object.id;
    const receiver_id = receiver_url.split('/').pop();

    async function handleAccept() {
        let putResponse = await foreignFollowPut(sender_url);
        if (!putResponse.ok) {
            console.log("Failed to accept friend request")
        } else {
            setRequestStatus("Accepted")
            await requestDelete(sender_url);
        }
    }

    async function handleDeny() {
        setRequestStatus("Declined")
        await requestDelete(sender_url);
    }

    return (
    <Box className='request' sx={{display: 'flex', justifyContent:'space-between', padding: '5px'}}>
        <Box style={{display: 'flex', alignItems: 'center'}}>
            <Avatar sx={{ml:'14px'}}src={request.actor.profileImage}/>
            <Typography sx={{textAlign: 'left', marginLeft: '10px', fontSize:'14px'}}>{request.actor.displayName}</Typography>
        </Box>
        <Box className="buttons" style={{ display: 'flex', marginLeft: '10px', gap: '-10px' }}>
            {requestStatus === 'Pending' ? (
                <>
                    <IconButton onClick={handleAccept}>
                        <CheckIcon/>
                    </IconButton>
                    <IconButton onClick={handleDeny}>
                        <CloseIcon/>
                    </IconButton>
                </>
            ) : (
                <Typography sx={{ mr:'14px', textAlign: 'center', alignSelf: 'center', fontSize: '14px' }}>
                    {requestStatus}
                </Typography>
            )}
        </Box>
    </Box>
  )
}

export default Request