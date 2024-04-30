import React from 'react'
import Feed from '../components/main/Feed'
import {RequireValidation} from "../components/RequireValidation";

const Home = () => {
    return (<RequireValidation>
        <div className="Home">
            <Feed/>
        </div>
    </RequireValidation>)
}

export default Home