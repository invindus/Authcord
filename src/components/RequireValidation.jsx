import {getUser} from "../lib/User";
import {useNavigate} from "react-router-dom";
import {useEffect} from "react";

export function RequireValidation(props) {
    const navigate = useNavigate();

    useEffect(() => {
        if (getUser() === null) {
            navigate("/sign_in");
        }
    }, [navigate]);

    return <>{props.children}</>
}