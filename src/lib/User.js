import base64 from "base-64";

let user = null;

export function setUser(newUser) {
  user = newUser;
  // Convert the user object to a string and store it in localStorage
  localStorage.setItem('user', JSON.stringify(newUser));
}

export function getUser() {
  // Try to get the user from memory first
  if (user) return user;
  
  // If not in memory, attempt to retrieve the user data from localStorage
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    user = JSON.parse(storedUser);
    return user;
  }

  // If there's no user in memory or localStorage, return null
  return null;
}


export function getBasicHeaderValue() {
  let user = getUser();
  if (user === null) {
    return null
  }
  let credentials = base64.encode(`${user.username}:${user.password}`);
  return 'Basic ' + credentials;
}