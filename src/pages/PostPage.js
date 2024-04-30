import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { getSinglePost } from '../lib/Posts';

import PostPageTemplate from '../components/main/PostPageTemplate';

const PostPage = () => {
  const { authorId, postId } = useParams();
  const [post, setPostData] = useState(null);


  useEffect(() => {  
    fetchPostData();
  }, [authorId, postId]);

  const fetchPostData = async () => {
    try {
      const postResponse = await getSinglePost(authorId, postId);
      const postWithComments = { ...postResponse[0].data, comments: postResponse[1].data.comments || [], likesCount: postResponse[2] };

      setPostData(postWithComments);

    } catch (error) {
      console.error('Failed to fetch post data:', error);
    }
  };

  if (!post) {
    return <div>Loading...</div>;
  }

  // Render post data
  return (
    <PostPageTemplate post={post}/>
  );
};


export default PostPage;
