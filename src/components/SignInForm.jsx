import * as React from "react";
import {useState} from "react";
import {Box, Button, CardMedia, Container, Divider, InputAdornment, TextField, Typography} from "@mui/material";
import ApiIcon from "@mui/icons-material/Api";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import PersonIcon from "@mui/icons-material/Person";
import LockIcon from "@mui/icons-material/Lock";
import img from "./image.png";
import {Link, useNavigate} from "react-router-dom";
import {setUser} from "../lib/User.js";
import {theme} from "../theme.js";


export default function SignInForm() {

    const navigate = useNavigate();

    async function signIn(username, password) {
        const response = await fetch("/authentication/login", {
            method: "POST", headers: {
                "Content-Type": "application/json",
            }, body: JSON.stringify({username, password}),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const accountData = await response.json();
        return accountData;
    }

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleSignIn = async () => {
        try {
            const response = await signIn(username, password);
            const accountData = {
                id: response.author_id,
                token: response.token,
                password: password,
                username: username,
                serverName: response.serverName,
                profileImage: response.profileImage,
            };
            setUser(accountData); // Store the user's data

            console.log("Sign in successful");
            localStorage.setItem("username", username);
            localStorage.setItem("password", password);
            localStorage.setItem("token", response.token);
            localStorage.setItem("authorId", response.author_id);
            localStorage.setItem("profileImage", response.profileImage);
            navigate(`/profile/${response.author_id}`); // Redirect to the profile page
        } catch (error) {
            console.error("Sign in failed:", error);
        }
    };

    return (
        <Container sx={{ display: "flex", flexDirection:"row", justifyContent: "center", alignItems: "center", height: "100vh" }}>
            <Container sx={{display:"flex", flexDirection:"column", width:'40%'}}>

                {/* LOGO */}
                <Box sx={{
                    display: "flex",
                    flexDirection: "row",
                    marginBottom: "15px",
                    alignItems: "center",
                }}>
                    <ApiIcon sx={{
                        color: theme.palette.primary.main,
                        padding: "10px",
                        fontWeight: 100,
                        width:'80px',
                        height:'80px',
                    }}/>
                    <Typography sx={{
                        color: theme.palette.primary.main,
                        fontSize: "40px",
                        fontWeight: 600,
                        letterSpacing: "3px",
                        padding: "10px",
                    }}>AUTHCORD</Typography>
                </Box>

                <Box sx={{display: "flex", flexDirection: "column", alignItems:'center', width:"100%"}}>
                    {/* USERNAME */}
                    <TextField
                        fullWidth
                        id="username"
                        label="Username"
                        variant="outlined"
                        onChange={e => setUsername(e.target.value)}
                        sx={{
                            mb:"30px",
                            "& .MuiOutlinedInput-root": {borderRadius: "20px"},
                            "& .MuiAutocomplete-input": {fontSize: "inherit"},  // for autocomplete smaller letters than intended bug
                        }}
                        InputProps={{
                            startAdornment: (<InputAdornment position="start">
                                    <PersonIcon sx={{color: theme.palette.primary.main}}/>
                                </InputAdornment>),
                        }}
                    />

                    {/* PASSWORD */}
                    <TextField
                        fullWidth
                        id="password"
                        label="Password"
                        type="password"
                        autoComplete="current-password"
                        onChange={e => setPassword(e.target.value)}
                        sx={{
                            mb: "30px",
                            "& .MuiOutlinedInput-root": {borderRadius: "20px"},
                            "& .MuiAutocomplete-input": {fontSize: "inherit"},
                        }}
                        InputProps={{
                            startAdornment: (<InputAdornment position="start">
                                    <LockIcon sx={{color: theme.palette.primary.main}}/>
                                </InputAdornment>),
                        }}
                    />

                    {/* SIGN IN */}
                    <Button variant="contained" onClick={handleSignIn} fullWidth sx={{
                        fontSize: "18px",
                        color: theme.palette.secondary.contrastText,
                        height: "50px",
                        borderRadius: "20px",
                        fontWeight: 600,
                    }}>
                        SIGN IN
                        <ExitToAppIcon sx={{marginLeft: "5px"}}/>
                    </Button>

                    <Divider sx={{ width:"80%", height:1, my: 2, color:theme.palette.primary.main}} />

                    {/* SIGN UP */}
                    <Button component={Link} to="/sign_up" variant="contained" sx={{
                        color: theme.palette.secondary.contrastText,
                        height: "30px",
                        width: "100px",
                        borderRadius: "10px",
                    }}>
                        SIGN UP
                    </Button>
                </Box>
            </Container>

            {/* BACKGROUND IMAGE */}
            <img src={img} alt="app logo" width={600}/>

        </Container>);
}
