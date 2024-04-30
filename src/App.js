import './App.css';
import {Routes, Route, useLocation, Navigate} from 'react-router-dom';
import { getUser } from './lib/User';

// Pages
import Home from './pages/Home';
import Profile from './pages/Profile';
import SignIn from './pages/Signin';
import SignUp from './pages/Signup';
import PostPage from './pages/PostPage';

// Components (./components/asdf)
// import LeftBar from './components/navbar/LeftBar';
// import RightBar from './components/navbar/RightBar';
import { useParams } from 'react-router-dom';
import {useEffect} from "react";
import TopBar from './components/navbar/TopBar';
import {fetchLocalWithBasic} from "./lib/Url";


function App() {
  useEffect(() => {
    document.title = 'Authcord';
    const fetchRemoteAuthors = async () => {
      try {
        const response = await fetchLocalWithBasic('/ext/remote_authors_scan');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const responseData = await response.json(); // Correctly wait for the JSON data
        console.log(responseData);
      } catch (error) {
        console.error("Failed to fetch remote authors:", error);
      }
    };

   
    fetchRemoteAuthors();
  }, []);

  const UserData = getUser()
  const location = useLocation();
  const isSignPage = location.pathname === "/sign_up" || location.pathname === "/sign_in";

  // If UserData is null and not already on a sign-in or sign-up page, redirect to sign-in
  if (!UserData && !isSignPage) {
    return <Navigate to="/sign_in" />;
  }


  return (
    <div className="App">
      {/* Render PermanentDrawerLeft and Right only if it's not the sign_up, sign_in pages */}
      {!isSignPage && <TopBar/>}

      <Routes>
        {/* Allow access only to sign-in and sign-up pages if UserData is null */}
        {UserData ? (
          <>
            <Route path="" element={<Home />} />
            <Route path="/profile/:id" element={<Profile />} />
            <Route path="/authors/:authorId/posts/:postId" element={<PostPage />} />
            <Route path="/sign_in" element={<SignIn />} />
            <Route path="/sign_up" element={<SignUp />} />
          </>
        ) : (
          <>
            <Route path="/authors/:authorId/posts/:postId" element={<PostPage />} />
            <Route path="/sign_in" element={<SignIn />} />
            <Route path="/sign_up" element={<SignUp />} />
          </>
        )}
      </Routes>

    </div>
  );
}

export default App;
