import type { UserRequest, UserRequestWithColors } from "@/types/user";

const addColorsToUsersRequests = (
  channelsColors: string[],
  userRequests: UserRequest[]
): UserRequestWithColors[] => {
  return userRequests.map((item, index) => {
    const assignedColor = channelsColors[index % channelsColors.length];
    return { ...item, color: assignedColor };
  });
};

export { addColorsToUsersRequests };
