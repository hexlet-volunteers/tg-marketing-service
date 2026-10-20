interface User {
  first_name: string;
  last_name: string;
  email: string;
}

interface UserNotificationSettings {
  weekly_reports: boolean;
  trend_notifications: boolean;
  limit_exceeded: boolean;
  new_features: boolean;
}

interface UserProfilePageProps {
  user: User;
  notifications: UserNotificationSettings | null;
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

export type { UserRequest, UserRequestWithColors, UserRequestProps, User, UserNotificationSettings, UserProfilePageProps }

