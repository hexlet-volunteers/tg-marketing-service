import { AppShell } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import React from 'react';
import { useLocation } from 'react-router-dom';
import { Footer } from './Footer';
import { Header } from './Header';
import { NavBar } from './NavBar';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [opened, { close, toggle }] = useDisclosure(false);
  const { pathname } = useLocation();
  const showSearchBar = pathname !== '/auth';

  return (
    <AppShell
      p={0}
      header={{ height: { base: 100, sm: 60 } }}
      navbar={{
        width: 260,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
    >
      <AppShell.Header>
        <Header opened={opened} onToggle={toggle} showSearchBar={showSearchBar} />
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <NavBar onClose={close} />
      </AppShell.Navbar>

      <AppShell.Main bg="gray.0" mih="100vh">
          {children}
        <Footer />
      </AppShell.Main>
    </AppShell>
  );
};

export default Layout;
