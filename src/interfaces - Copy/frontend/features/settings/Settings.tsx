import React, { useState } from 'react';
import {
    Box,
    Button,
    Divider,
    FormControl,
    FormLabel,
    Heading,
    Input,
    Switch,
    VStack,
    HStack,
    useToast,
    Select,
    Tabs,
    TabList,
    TabPanels,
    Tab,
    TabPanel,
    Text,
} from '@chakra-ui/react';
import { useApi } from '../../hooks/useApi';

export const Settings: React.FC = () => {
    const toast = useToast();
    const api = useApi();

    // General settings
    const [username, setUsername] = useState('user@example.com');
    const [language, setLanguage] = useState('en');
    const [theme, setTheme] = useState('system');

    // Security settings
    const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
    const [dataEncryption, setDataEncryption] = useState(true);

    // AI settings
    const [modelPrecision, setModelPrecision] = useState('high');
    const [gpuAcceleration, setGpuAcceleration] = useState(true);
    const [maxTokens, setMaxTokens] = useState('2048');

    const handleSaveGeneral = () => {
        // In a real implementation, this would call an API
        toast({
            title: 'Settings saved',
            status: 'success',
            duration: 3000,
            isClosable: true,
        });
    };

    const handleSaveSecurity = () => {
        toast({
            title: 'Security settings updated',
            status: 'success',
            duration: 3000,
            isClosable: true,
        });
    };

    const handleSaveAI = () => {
        toast({
            title: 'AI settings updated',
            status: 'success',
            duration: 3000,
            isClosable: true,
        });
    };

    return (
        <Box>
            <Heading size="md" mb={6}>Settings</Heading>

            <Tabs colorScheme="brand" isLazy>
                <TabList>
                    <Tab>General</Tab>
                    <Tab>Security</Tab>
                    <Tab>AI Configuration</Tab>
                </TabList>

                <TabPanels>
                    <TabPanel>
                        <VStack spacing={6} align="start">
                            <FormControl>
                                <FormLabel>Email Address</FormLabel>
                                <Input
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </FormControl>

                            <FormControl>
                                <FormLabel>Language</FormLabel>
                                <Select
                                    value={language}
                                    onChange={(e) => setLanguage(e.target.value)}
                                >
                                    <option value="en">English</option>
                                    <option value="es">Spanish</option>
                                    <option value="fr">French</option>
                                    <option value="de">German</option>
                                    <option value="ja">Japanese</option>
                                </Select>
                            </FormControl>

                            <FormControl>
                                <FormLabel>Theme</FormLabel>
                                <Select
                                    value={theme}
                                    onChange={(e) => setTheme(e.target.value)}
                                >
                                    <option value="system">System Default</option>
                                    <option value="light">Light</option>
                                    <option value="dark">Dark</option>
                                </Select>
                            </FormControl>

                            <Button colorScheme="brand" onClick={handleSaveGeneral}>
                                Save Changes
                            </Button>
                        </VStack>
                    </TabPanel>

                    <TabPanel>
                        <VStack spacing={6} align="start">
                            <FormControl display="flex" alignItems="center">
                                <FormLabel mb="0">
                                    Two-Factor Authentication
                                </FormLabel>
                                <Switch
                                    colorScheme="brand"
                                    isChecked={twoFactorEnabled}
                                    onChange={() => setTwoFactorEnabled(!twoFactorEnabled)}
                                />
                            </FormControl>

                            <FormControl display="flex" alignItems="center">
                                <FormLabel mb="0">
                                    Enhanced Data Encryption
                                </FormLabel>
                                <Switch
                                    colorScheme="brand"
                                    isChecked={dataEncryption}
                                    onChange={() => setDataEncryption(!dataEncryption)}
                                />
                            </FormControl>

                            <Divider />

                            <Text>
                                Last login: {new Date().toLocaleString()}
                            </Text>

                            <Button colorScheme="brand" onClick={handleSaveSecurity}>
                                Save Security Settings
                            </Button>
                        </VStack>
                    </TabPanel>

                    <TabPanel>
                        <VStack spacing={6} align="start">
                            <FormControl>
                                <FormLabel>Model Precision</FormLabel>
                                <Select
                                    value={modelPrecision}
                                    onChange={(e) => setModelPrecision(e.target.value)}
                                >
                                    <option value="low">Low (Faster)</option>
                                    <option value="medium">Medium (Balanced)</option>
                                    <option value="high">High (More Accurate)</option>
                                </Select>
                            </FormControl>

                            <FormControl>
                                <FormLabel>Maximum Tokens</FormLabel>
                                <Input
                                    value={maxTokens}
                                    onChange={(e) => setMaxTokens(e.target.value)}
                                    type="number"
                                />
                            </FormControl>

                            <FormControl display="flex" alignItems="center">
                                <FormLabel mb="0">
                                    GPU Acceleration
                                </FormLabel>
                                <Switch
                                    colorScheme="brand"
                                    isChecked={gpuAcceleration}
                                    onChange={() => setGpuAcceleration(!gpuAcceleration)}
                                />
                            </FormControl>

                            <Text fontSize="sm" color="gray.500">
                                Note: GPU acceleration requires compatible hardware.
                                Current GPU: NVIDIA GeForce GTX 1050 Ti (4GB VRAM)
                            </Text>

                            <Button colorScheme="brand" onClick={handleSaveAI}>
                                Save AI Settings
                            </Button>
                        </VStack>
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </Box>
    );
};
