import {createTheme} from "@mui/material";

export const theme = createTheme({
    palette: {
        primary: {
            main: "#FCCF8C",
        }, secondary: {
            main: "#3F3B37",
        }, badgeColor: {
            main: "#EC5F4C",
        },
    },
});

export const altTheme = createTheme({
    palette: {
        mode: "dark", primary: {
            main: "#FCCF8C",
        }, secondary: {
            main: "#3F3B37",
        }, badgeColor: {
            main: "#EC5F4C",
        },
    },
});
