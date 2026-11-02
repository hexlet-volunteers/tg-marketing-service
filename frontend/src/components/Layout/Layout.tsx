import { AppShell } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import React from 'react';
import { usePage } from '@inertiajs/react';
import { Footer } from './Footer';
import  Header from './Header';
import { NavBar } from './NavBar';

const Layout: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  const [opened, { close, toggle }] = useDisclosure(false);
  const { url } = usePage();
  const pathname = url.split('?')[0];
  const showSearchBar = pathname !== '/auth/login/';

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
