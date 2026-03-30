import React from 'react';
import { Box, Flex, Tabs, TabList, TabPanels, Tab, TabPanel, useColorModeValue } from '@chakra-ui/react';
import { Header } from './components/Header';
import { Chat } from './features/chat/Chat';
import { Datasets } from './features/datasets/Datasets';
import { Models } from './features/models/Models';
import { Settings } from './features/settings/Settings';

const App: React.FC = () => {
    const bgColor = useColorModeValue('gray.50', 'gray.800');

    return (
        <Box minH="100vh" bg={bgColor}>
            <Header />
            <Flex as="main" flexDirection="column" maxW="1200px" mx="auto" p={4}>
                <Tabs variant="enclosed" colorScheme="brand" isLazy>
                    <TabList>
                        <Tab>Chat</Tab>
                        <Tab>Datasets</Tab>
                        <Tab>Models</Tab>
                        <Tab>Settings</Tab>
                    </TabList>
                    <TabPanels>
                        <TabPanel>
                            <Chat />
                        </TabPanel>
                        <TabPanel>
                            <Datasets />
                        </TabPanel>
                        <TabPanel>
                            <Models />
                        </TabPanel>
                        <TabPanel>
                            <Settings />
                        </TabPanel>
                    </TabPanels>
                </Tabs>
            </Flex>
        </Box>
    );
};

export default App;
