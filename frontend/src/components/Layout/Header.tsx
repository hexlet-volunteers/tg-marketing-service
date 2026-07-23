import { Avatar, Box, Burger, Button, Flex, Text, Title } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { SearchBar } from '../ui/SearchBar';

interface HeaderProps {
    opened: boolean;
    onToggle: () => void;
    showSearchBar?: boolean;
}

export function Header({ opened, onToggle, showSearchBar = true }: HeaderProps) {
    const navigate = useNavigate();

    return (
        <Flex px="md" py="sm" gap="sm" justify="space-between">
            <Box>
                <Burger
                    hiddenFrom="sm"
                    opened={opened}
                    onClick={onToggle}
                />

                <Box visibleFrom="sm">
                    <Flex gap="sm" align="center">
                        <Avatar color="tgblue" radius="md">t</Avatar>
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
                    <Button variant="subtle" onClick={() => navigate('/auth')}>Войти</Button>
                    <Text>Мария Л.</Text>
                    <Avatar color="pink">M</Avatar>
                </Flex>
            </Flex>
        </Flex>
    )

}