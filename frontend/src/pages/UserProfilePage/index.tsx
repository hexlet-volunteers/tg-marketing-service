import UserProfilePage from './ui/UserProfilePage';
import { mockUser, mockNotifications } from '@/shared/mocks/user';

const UserProfilePageContainer = () => <UserProfilePage user={ mockUser } notifications={ mockNotifications }/>;

export default UserProfilePageContainer;
