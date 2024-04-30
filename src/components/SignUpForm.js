import * as React from "react";
import {useState} from "react";
import {Box, Button, Container, Divider, InputAdornment, TextField, Typography} from "@mui/material";
import ApiIcon from "@mui/icons-material/Api";
import EmailIcon from "@mui/icons-material/Email";
import PersonIcon from "@mui/icons-material/Person";
import LockIcon from "@mui/icons-material/Lock";
import img from "./image.png";
import {Link, useNavigate} from "react-router-dom";
import {theme} from "../theme.js";

export default function SignUpForm() {

    const navigate = useNavigate();
    
    const [form, setForm] = useState({ email: '', password: '', username: ''});

    const handleChange = (event) => {
        setForm({
            ...form,
            [event.target.name]: event.target.value
        });
    };

    const handleSubmit = (event) => {
        event.preventDefault();

        fetch("/authentication/signup", {
            headers: {
                'Content-Type': 'application/json',
            },

            method: "POST",
            body: JSON.stringify(form)
        })
        .then(response => response.json())
        .then(data => {
            // Handle response data
            console.log(data);
            navigate("/sign_in");

        })
        .catch(error => {
            // Handle error
            console.error('Error:', error);
        });
    };
  
    return (
        <Container sx={{ display: "flex", flexDirection:"row", justifyContent: "center", alignItems: "center", height: "100vh" }}>
            <Container sx={{display:"flex", flexDirection:"column", width:'40%', mt:-10}}>

            {/* LOGO */}
            <Box sx={{display:'flex', marginTop:'70px', marginLeft:'10px', marginBottom:'15px', alignItems:'center'}}>
                <ApiIcon sx={{color: theme.palette.primary.main, padding:"10px", fontWeight:100, width:"80px", height:"80px"}}/>
                <Typography sx={{color: theme.palette.primary.main, fontSize:'40px', fontWeight:600, letterSpacing:'3px', padding:'10px'}}>AUTHCORD</Typography>
            </Box>

            <Box sx={{display:'flex', flexDirection:'column'}}>
                <form onSubmit={handleSubmit}>

                        {/* EMAIL */}
                        <TextField 
                            id="email" 
                            name="email"
                            label="Email" 
                            variant="outlined"
                            value={form.email} onChange={handleChange}
                            fullWidth
                            sx={{
                                mb:"30px",
                                '& .MuiOutlinedInput-root': {borderRadius: '20px'}, 
                                '& .MuiAutocomplete-input': {fontSize: 'inherit'},  // for autocomplete smaller letters than intended bug
                            }}
                            InputProps={
                                {startAdornment: (
                                    <InputAdornment position="start">
                                        <EmailIcon sx={{color: theme.palette.primary.main}}/>
                                    </InputAdornment>
                            )}}
                        />
                    
                    {/* USERNAME */}
                        <TextField 
                            id="username" 
                            name="username"
                            label="Username" 
                            variant="outlined"
                            value={form.username} onChange={handleChange}
                            fullWidth
                            sx={{
                                mb:"30px",
                                '& .MuiOutlinedInput-root': {borderRadius: '20px'}, 
                                '& .MuiAutocomplete-input': {fontSize: 'inherit'},
                            }}
                            InputProps={
                                {startAdornment: (
                                    <InputAdornment position="start">
                                        <PersonIcon sx={{color: theme.palette.primary.main}}/>
                                    </InputAdornment>
                            )}}
                        />

                    {/* PASSWORD */}
                        <TextField 
                            id="password"
                            name="password"
                            label="Password"
                            type="password"
                            autoComplete="current-password"
                            value={form.password} onChange={handleChange}
                            fullWidth
                            sx={{
                                mb:'30px',
                                '& .MuiOutlinedInput-root': {borderRadius: '20px'}, 
                                '& .MuiAutocomplete-input': {fontSize: 'inherit'},
                            }}
                            InputProps={
                                {startAdornment: (
                                    <InputAdornment position="start">
                                        <LockIcon sx={{color: theme.palette.primary.main}}/>
                                    </InputAdornment>
                            )}}
                        />

                    {/* SIGN UP */}
                        <Button type="submit" variant="contained" fullWidth sx={{
                            fontSize: "18px",
                            color: theme.palette.secondary.contrastText,
                            height: "50px",
                            borderRadius: "20px",
                            fontWeight: 600,
                            mb:'30px'
                        }}>
                        SIGN UP
                    </Button>
                </form>

                {/* Return to Sign In */}
                <Box sx={{marginBottom: '10px', display:'flex', flexDirection:'column',width:'100%', alignItems:'center'}}>
                    <Divider sx={{ bgcolor: 'primary.main',height: '0.5px', width:'80%', borderRadius: '10px', marginBottom: '10px'}}/>
                    <Box display='flex' flexDirection='row' gap={1} sx={{alignItems:'center'}}>
                        <Typography fontSize='14px'>Already registered?</Typography>
                        <Link to="/sign_in" style={{textDecoration: 'none', fontSize:'14px'}}>Sign In</Link>
                    </Box>
                </Box>

            </Box>
        </Container>

        <img src={img} alt="app logo" width={600}/>

    </Container>
  );
}