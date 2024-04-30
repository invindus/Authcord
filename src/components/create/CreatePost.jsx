import React, {useContext, useState} from "react";
import {
    Box,
    Button,
    Card,
    Container,
    darken,
    Divider,
    FormControl,
    FormControlLabel,
    FormLabel,
    IconButton,
    Radio,
    RadioGroup,
    Snackbar,
    TextField,
    Toolbar,
    Typography,
    useTheme,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import TextFormatIcon from "@mui/icons-material/TextFormat";
import GroupsIcon from "@mui/icons-material/Groups";
import GroupIcon from "@mui/icons-material/Group";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import ImageIcon from "@mui/icons-material/Image";
import {useForm} from "react-hook-form";
import {getUser} from "../../lib/User";
import {postData, postFriendsInbox, postPublicInbox, shareToFollowers} from "../../lib/Posts";
import {AltThemeContext} from "../../index";


const CreatePost = ({handleCreateClose}) => {
    const theme = useTheme();
    const {useAltTheme} = useContext(AltThemeContext);
    const {register, handleSubmit: handleSubmitText, reset} = useForm();
    const [error, setError] = useState("");
    const [imgError, setImgError] = useState("");
    const [imageUrl, setImageUrl] = useState("");
    const [snackbarOpen, setSnackbarOpen] = useState(false);
    const [formData, setFormData] = useState({
        title: "", description: "", content: "", contentType: "", visibility: "",
    });
    const BASE_URL = window.location.origin;        // in heroku, axios sends request to localhost instead of domain. this gets the current heroku domain.

    const authorId = getUser().id;

    const convertBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const fileReader = new FileReader();
            fileReader.readAsDataURL(file);

            fileReader.onload = () => {
                const result = fileReader.result;
                // MIME type prefix and base64 data
                const [prefix, base64Data] = result.split(",");
                resolve({prefix, base64Data});
            };

            fileReader.onerror = (error) => {
                reject(error);
            };
        });
    };

    const uploadImage = async (event) => {
        const imgFile = event.target.files[0];
        const {prefix, base64Data} = await convertBase64(imgFile);

        setFormData({...formData, contentType: prefix.split(":")[1], content: base64Data});
        if (imgError === "Please select an image to upload.") {
            setImgError("");
        }

    };

    const handleSubmitImage = async (event) => {
        event.preventDefault();

        // Required fields check
        if (formData.content.trim() === "") {
            setImgError("Please select an image to upload.");
            return;
        } else if (formData.title.trim() === "") {
            setImgError("Title is required.");
            return;
        } else if (formData.description.trim() === "") {
            setImgError("Description is required.");
            return;
        } else if (formData.visibility.trim() === "") {
            setImgError("Visibility is required.");
            return;
        }


        const response = await postData(authorId, formData);

        // Send image post to inbox
        if (formData.visibility === "PUBLIC") {
            await postPublicInbox(authorId, response);
        } else if (formData.visibility === 'FRIENDS'){
            await postFriendsInbox(authorId, response)
        }

        const post_id = response.data.id;
        // axios returns localhost domain name, extracting path after localhost to append to heroku domain
        const extractPath = post_id.substring(post_id.indexOf("/api/authors"));

        setImageUrl(BASE_URL + extractPath + "/image");

        // return back to public so user doesn't accidentally submit UNLISTED
        setFormData({...formData, visibility: "PUBLIC"});
    };

    const handleCopyToClipboard = () => {
        navigator.clipboard.writeText(imageUrl);
        handleSnackbarOpen();
    };

    const handleSnackbarOpen = () => {
        setSnackbarOpen(true);
      };
      
      const handleSnackbarClose = () => {
        setSnackbarOpen(false);
      };

    const handleSubmitTextContent = async (data) => {
        setFormData({...formData, ...data});

        // Required fields check
        if (formData.title.trim() === "") {
            setError("Title is required.");
            return;
        } else if (formData.description.trim() === "") {
            setError("Description is required.");
            return;
        } else if (formData.content.trim() === "") {
            setError("Content is required to submit.");
            return;
        }
        // Check contentType is PNG or JPEG for image post
        else if (formData.contentType === "image/png;base64" || formData.contentType === "image/jpeg;base64" || formData.contentType === "") {
            setError("Content Type is required.");
            return;
        } else if (formData.visibility === "") {
            setError("Visibility is required.");
            return;
        }

        const response = await postData(authorId, formData);
        // console.log(response.data)
        // await shareToFollowers(authorId, response);

        if (formData.visibility === "PUBLIC") {
            await postPublicInbox(authorId, response);
        } else if (formData.visibility === 'FRIENDS'){
            await postFriendsInbox(authorId, response)
        }

        handleCreateClose();
        reset();
        window.location.reload();
    };


    return (<Container sx={{
            display: "flex",
            flexDirection: "column",
            width: "50%",
            height:"100%",
            color: theme.palette.text.primary,
            borderRadius: "10px",
            alignItems: "center",
            // border: useAltTheme ? `1px solid ${theme.palette.text.secondary}` : "none",
            mt:8
        }}>
            <Container>
            <form onSubmit={handleSubmitText(handleSubmitTextContent)}>
                <Box sx={{
                    display: "flex",
                    flexDirection: "row",
                    alignItems: "center",
                    width:"100%",
                    height: "50px",
                    justifyContent: "space-between",
                    color: theme.palette.secondary.contrastText,
                    background: theme.palette.secondary.main,
                    p: 1,
                    borderTopLeftRadius: "10px",
                    borderTopRightRadius: "10px",
                }}>
                    <IconButton onClick={handleCreateClose}><ArrowBackIcon
                        sx={{color: theme.palette.secondary.contrastText}}/></IconButton>
                    <Typography variant="h6">Create a new post</Typography>

                    <Button type="submit" variant="contained" sx={{
                        width: "120px",
                        height: "25px",
                        borderRadius: "10px",
                        ml: -10,
                        mr: 1,
                        color: theme.palette.primary.contrastText,
                        background: theme.palette.primary.main,
                        "&:hover": {
                            background: darken(theme.palette.primary.main, 0.2),
                        },
                    }}>
                        Submit
                    </Button>

                </Box>

                {/* Show error if required field empty. */}
                {error && 
                    <Container sx={{display:'flex', flexDirection:'column', alignItems:'center', width:"100%", backgroundColor: theme.palette.background.default}}>
                        <Typography variant="body2" color="error" sx={{mt: 1, fontWeight: 600}}>{error}</Typography>
                    </Container>
                }

                <Container sx={{
                    backgroundColor: theme.palette.background.default, color: theme.palette.text.primary, p:1, borderBottomLeftRadius:'10px', borderBottomRightRadius:'10px',
                }}>
                    <Box sx={{display: "flex", flexDirection: "column", alignItems: "center", width: "100%"}}>
                        {/* Title */}
                        <TextField
                            required fullWidth
                            label="Title" variant="outlined" margin="dense"
                            sx={{
                                "& .MuiOutlinedInput-root": {
                                    borderRadius: "10px",
                                },
                            }}
                            {...register("title", {required: true})}
                            value={formData.title}
                            onChange={(e) => {
                                setFormData({...formData, title: e.target.value});
                                // Separate because can have different errors and will still clear if using "if imgError || error "
                                if (imgError === "Title is required.") {
                                    setImgError("");
                                }
                                if (error === "Title is required.") {
                                    setError("");
                                }
                            }}
                        />

                        {/* Description */}
                        <TextField
                            required fullWidth
                            label="Description" variant="outlined" margin="dense"
                            sx={{
                                "& .MuiOutlinedInput-root": {
                                    borderRadius: "10px",
                                },
                            }}
                            {...register("description", {required: true})}
                            value={formData.description}
                            onChange={(e) => {
                                setFormData({...formData, description: e.target.value});
                                if (imgError === "Description is required.") {
                                    setImgError("");
                                }
                                if (error === "Description is required.") {
                                    setError("");
                                }
                            }}
                        />

                        {/* Content */}
                        <TextField
                            id="content_field"
                            fullWidth multiline rows={4}
                            label="Content" variant="outlined" margin="dense"
                            sx={{
                                "& .MuiOutlinedInput-root": {
                                    borderRadius: "10px",
                                },
                            }}
                            {...register("content", {required: true})}
                            onChange={(e) => {
                                setFormData({...formData, content: e.target.value});
                                if (error === "Content is required.") {
                                    setError("");
                                }
                            }}
                        />
                    </Box>

                    <Card variant="outlined" sx={{
                        borderRadius: "10px",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        my: 1,

                    }}>
                        <Box>
                            {/* Visibility Selection */}
                            <FormControl component="fieldset" margin="normal">
                                <FormLabel component="legend">Visibility</FormLabel>
                                <RadioGroup required row name="visibility" value={formData.visibility} sx={{gap: 3, mr:1}}
                                            onChange={(e) => {
                                                setFormData({...formData, visibility: e.target.value});
                                                if (imgError === "Visibility is required.") {
                                                    setImgError("");
                                                }
                                                if (error === "Visibility is required.") {
                                                    setError("");
                                                }
                                            }}>
                                    <FormControlLabel value="PUBLIC" control={<Radio/>} labelPlacement="start"
                                                      label={<Box sx={{display: "flex", alignItems: "center"}}>
                                                          <GroupsIcon sx={{mr: 1}}/>
                                                          Public
                                                      </Box>}/>
                                    <FormControlLabel value="FRIENDS" control={<Radio/>} labelPlacement="start"
                                                      label={<Box sx={{display: "flex", alignItems: "center"}}>
                                                          <GroupIcon sx={{mr: 1}}/>
                                                          Friends
                                                      </Box>}/>
                                    <FormControlLabel value="UNLISTED" control={<Radio/>} labelPlacement="start"
                                                      label={<Box sx={{display: "flex", alignItems: "center"}}>
                                                          <VisibilityOffIcon sx={{mr: 1}}/>
                                                          Unlisted
                                                      </Box>}/>
                                </RadioGroup>
                            </FormControl>
                        </Box>

                        <Divider sx={{width: "90%"}}/>

                        <Box>
                            {/* Content Type Selection */}
                            <FormControl component="fieldset" margin="normal">
                                <FormLabel component="legend">Content Type</FormLabel>
                                <RadioGroup required row name="contentType" value={formData.contentType} sx={{gap: 2}}
                                            onChange={(e) => {
                                                setFormData({...formData, contentType: e.target.value});
                                                if (error === "Content Type is required.") {
                                                    setError("");
                                                }
                                            }}>
                                    <FormControlLabel value="text/plain" control={<Radio/>} labelPlacement="start"
                                                      label={<Box sx={{display: "flex", alignItems: "center"}}>
                                                          <TextFormatIcon sx={{mr: 1}}/>
                                                          Plain Text
                                                      </Box>}/>
                                    <FormControlLabel value="text/markdown" control={<Radio/>} labelPlacement="start"
                                                      label={<Box sx={{display: "flex", alignItems: "center"}}>
                                                          <ImageIcon sx={{mr: 1}}/>
                                                          Markdown
                                                      </Box>}/>
                                </RadioGroup>
                            </FormControl>
                        </Box>
                    </Card>
                </Container>
            </form>
            </Container>

            <Container sx={{mt:1}}>
                <Box sx={{
                    color: theme.palette.secondary.contrastText,
                    background: theme.palette.secondary.main,
                    width: "100%",
                    height: "30px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    borderTopLeftRadius:'10px',
                    borderTopRightRadius:'10px',
                }}>
                    <Typography>Upload an Image</Typography>
                </Box>
                {/* UPLOAD IMAGE */}
                <Card variant="outlined" sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    borderTopLeftRadius: "-15px",
                    borderTopRightRadius: "-15px",
                    mb: 2,
                }}>
                    <form onSubmit={handleSubmitImage}>
                        <Box sx={{display: "flex", flexDirection: "row", alignItems: "center", my: 1}}>
                            <input type="file" onChange={(e) => {
                                uploadImage(e);
                            }}/>

                            <Button type="submit" variant="contained" sx={{
                                background: theme.palette.primary.main,
                                color: theme.palette.primary.contrastText,
                                width: "150px",
                                height: "30px",
                                borderRadius: "10px",
                                "&:hover": {
                                    background: darken(theme.palette.primary.main, 0.2),
                                },
                            }}>
                                Upload Image
                            </Button>
                        </Box>
                    </form>

                    <Divider sx={{my: 1, width: "90%"}}/>

                    {imgError ? (<Typography variant="body2" color="error"
                                                sx={{fontWeight: 600, mb: 1}}>{imgError}</Typography>) : (imageUrl && (<>
                                <Typography sx={{fontWeight: 600}}> Insert image link in Markdown </Typography>
                                <Button variant="contained" onClick={handleCopyToClipboard} sx={{
                                    width: "120px",
                                    height: "25px",
                                    borderRadius: "10px",
                                    mb:2,
                                    color: theme.palette.primary.contrastText,
                                    background: theme.palette.primary.main,
                                    "&:hover": {
                                        background: darken(theme.palette.primary.main, 0.2),
                                    }
                                }}>
                                    Copy Link
                                </Button>
                                

                            </>))}
                </Card>
            </Container>

            <Snackbar
            open={snackbarOpen}
            autoHideDuration={6000}
            onClose={handleSnackbarClose}
            message="Link copied to clipboard."
            />
        
        </Container>

    );
};

export default CreatePost;

