interface User {
  first_name: string;
  last_name: string;
  email: string;
}

interface UserNotification {
  label: string;
  defaultChecked: boolean;
}

interface UserProfilePageProps {
  user: User;
  notifications: UserNotification[] | null;
}

interface UserRequest {
  title: string;
  username: string;
  author: string;
  time: string;
  category: string;    
}

interface UserRequestWithColors extends UserRequest {
  color: string;
}

interface UserRequestProps {
  userRequests: UserRequestWithColors[];
}

export type { UserRequest, UserRequestWithColors, UserRequestProps, User, UserNotification, UserProfilePageProps }

