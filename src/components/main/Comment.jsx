import {Avatar, Box, Divider, Typography} from "@mui/material";
import React from "react";
import ReactMarkdown from "react-markdown";
import LikeButton from "./LIkeButton";

export default function Comment({comment}) {
    return (
    <Box sx={{display:'flex', flexDirection:'column', alignItems:'center', width:'100%', mt:1}}>
        <Box sx={{display:'flex', flexDirection:'row', alignitems:'center', width:'100%', justifyContent:'space-between'}}>
            <Box sx={{display:'flex', flexDirection:'row', alignItems:'center', width:'70%', ml:2}}>
                <Avatar src={comment.author.profileImage}/>
                <Typography sx={{ml:1, mr:2, fontWeight:600}}>{comment.author.displayName}</Typography>
                <Box sx={{ textAlign: 'start', overflowWrap: 'break-word', maxWidth:"100%"}}>
                    <ReactMarkdown>{comment.comment}</ReactMarkdown>
                </Box>
            </Box>
            {comment.id.includes("uddit-619bef50b90e.herokuapp.com/") ? <></> :
                <LikeButton sx={{mr: 2}} object={comment} type="comment"/>}
        </Box>
        <Divider sx={{width:'100%', mt:1}}/>
    </Box>
    );
}
