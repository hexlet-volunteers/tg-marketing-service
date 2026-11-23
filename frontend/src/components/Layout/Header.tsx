import { Avatar, Box, Burger, Button, Flex, Text, Title } from "@mantine/core";
import { router, usePage } from "@inertiajs/react";
import { IconLogout } from "@tabler/icons-react";
import { SearchBar } from "../ui/SearchBar";
import { initials } from "@/utils/initials";
import type { SharedPageProps } from "@/types/auth";

interface HeaderProps {
 opened: boolean;
 onToggle: () => void;
 showSearchBar?: boolean;
}

const Header = ({ opened, onToggle, showSearchBar = true }: HeaderProps) => {
 const { auth } = usePage<SharedPageProps>().props;

 return (
  <Flex px="md" py="sm" gap="sm" justify="space-between">
   <Box>
    <Burger hiddenFrom="sm" opened={opened} onClick={onToggle} />

    <Box visibleFrom="sm">
     <Flex gap="sm" align="center">
      <Avatar color="tgblue" radius="md">
       t
      </Avatar>
      <Title order={3}>tgpulse</Title>
     </Flex>
    </Box>
   </Box>

   <Flex wrap="wrap-reverse" gap="5px">
    {showSearchBar && (
     <Box flex="1 1 0" miw="300">
      <SearchBar />
     </Box>
    )}
    <Flex align="center" gap="sm" ml="auto" style={{ flexShrink: 0 }}>
     {auth ? (
      <>
       <Text>{auth.name}</Text>
       <Avatar src={auth.avatar_url || undefined} color="pink">
        {initials(auth.name)}
       </Avatar>
       <Button
        variant="subtle"
        color="tgred"
        leftSection={<IconLogout size={16} />}
        onClick={() => router.post("/auth/logout/")}
       >
        Выйти
       </Button>
      </>
     ) : (
      <Button variant="subtle" onClick={() => router.visit("/auth/login/")}>
       Войти
      </Button>
     )}
    </Flex>
   </Flex>
  </Flex>
 );
};

export default Header;
