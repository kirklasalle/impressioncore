import React from 'react';
import { Box, Flex, Heading, IconButton, useColorMode, useColorModeValue } from '@chakra-ui/react';
import { FaMoon, FaSun } from 'react-icons/fa';

export const Header: React.FC = () => {
    const { colorMode, toggleColorMode } = useColorMode();
    const bgColor = useColorModeValue('white', 'gray.800');
    const borderColor = useColorModeValue('gray.200', 'gray.700');

    return (
        <Box as="header" bg={bgColor} borderBottom="1px" borderColor={borderColor} py={4} px={6}>
            <Flex justify="space-between" align="center" maxW="1200px" mx="auto">
                <Heading as="h1" size="md">ImpressionCore</Heading>
                <IconButton
                    aria-label="Toggle dark mode"
                    icon={colorMode === 'light' ? <FaMoon /> : <FaSun />}
                    onClick={toggleColorMode}
                    variant="ghost"
                />
            </Flex>
        </Box>
    );
};
