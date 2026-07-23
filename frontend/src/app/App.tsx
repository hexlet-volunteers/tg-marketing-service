import { BrowserRouter as Router } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { theme } from './theme';
import Layout from '@/components/Layout/Layout';
import { renderRoutes } from './routes';

const App: React.FC = () => {
  return (
    <MantineProvider theme={theme}>
      <Router>
        <Layout>
          {renderRoutes()}
        </Layout>
      </Router>
    </MantineProvider>
  );
};

export default App;
