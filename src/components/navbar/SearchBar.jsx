import {Box, InputAdornment, List, ListItem, ListItemButton, ListItemText, TextField, useTheme} from "@mui/material";
import {alpha} from "@mui/material/styles";
import SearchIcon from "@mui/icons-material/Search";
import React, {useContext, useEffect, useRef, useState} from "react";
import {getUser} from "../../lib/User";
import {useNavigate} from "react-router-dom";
import {AltThemeContext} from "../../index";

const SearchBar = () => {
    const navigate = useNavigate();
    const searchRef = useRef(null);

    const theme = useTheme();
    const {useAltTheme} = useContext(AltThemeContext);

    const [authors, setAuthors] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const pageSize = 200;
    const [query, setQuery] = useState("");
    const [filteredAuthors, setFilteredAuthors] = useState([]);
    const [showResults, setShowResults] = useState(false);
    const currentUser = getUser().username;

    // Hide results after clicking outside of results
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (searchRef.current && !searchRef.current.contains(event.target)) {
                setShowResults(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    // Reshow results when clicking back onto search bar
    useEffect(() => {
        const handleFocus = () => {
            if (query && searchRef.current.contains(document.activeElement)) {
                setShowResults(true);
            }
        };

        document.addEventListener("focusin", handleFocus);
        return () => {
            document.removeEventListener("focusin", handleFocus);
        };
    }, [query]);

    const handlenav = (e, id) => {
        e.stopPropagation();
        const auth_id = (id[id.length] === "/" ? id.substring(0, id.length - 1) : id).split("/").pop();
        navigate(`/profile/${auth_id}`);
        setQuery("");
    };

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await fetch(`/api/authors/?local&page=${currentPage}&size=${pageSize}`);
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                const data = await response.json();
                console.log(currentUser);
                setAuthors(data.items || []);
            } catch (error) {
                console.error("Failed to fetch users:", error);
            }
        };

        fetchUsers();
    }, []);

    useEffect(() => {
        const filtered = authors.filter((author) => author.displayName.toLowerCase().includes(query.toLowerCase()) && author.displayName !== currentUser);
        setFilteredAuthors(filtered);
    }, [authors, query]);

    return (<Box ref={searchRef} sx={{
            position: "relative",
            borderRadius: "10px",
            backgroundColor: alpha(theme.palette.background.default, 0.70),
            "&:hover": {
                backgroundColor: alpha(theme.palette.background.default, 0.90),
            },
            mr: 2,
            ml: 0,
            height: "40px",
            width: "400px",
        }}>
            <TextField
                fullWidth
                id="Search"
                variant="outlined"
                placeholder="Search"
                InputProps={{
                    style: {height: "40px", borderRadius: "10px"}, startAdornment: (<InputAdornment position="start">
                            <SearchIcon/>
                        </InputAdornment>),
                }}
                value={query}
                onChange={(e) => {
                    setQuery(e.target.value);
                    setShowResults(true);
                }}
            />
            {showResults && query && (<Box sx={{
                    position: "absolute",
                    top: "100%",
                    left: 0,
                    right: 0,
                    maxHeight: 400,
                    overflowY: "auto",
                    zIndex: 1,
                    background: theme.palette.background.default,
                    borderRadius: "10px",
                    boxShadow: "0px 2px 5px rgba(0, 0, 0, 0.1)",
                    mt: "2px",
                    border: useAltTheme ? `1px solid ${theme.palette.text.secondary}` : "none",
                }}>
                    <List>
                        {filteredAuthors.map((author) => (<ListItem key={author.id}>
                                <ListItemButton sx={{p: 0.5, "&:hover": {borderRadius: "10px"}}}
                                                onClick={(e) => handlenav(e, author.id)}>
                                    <ListItemText primary={author.displayName}
                                                  sx={{color: theme.palette.text.primary}}/>
                                </ListItemButton>
                            </ListItem>))}
                    </List>

                </Box>)}
        </Box>);
};

export default SearchBar;