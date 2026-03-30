import React, { useState } from 'react';
import {
    Box,
    Input,
    Button,
    VStack,
    HStack,
    Text,
    useColorModeValue,
    Flex,
} from '@chakra-ui/react';

type Message = {
    id: string;
    text: string;
    sender: 'user' | 'assistant';
    timestamp: Date;
};

export const Chat: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');

    const userBgColor = useColorModeValue('blue.50', 'blue.900');
    const assistantBgColor = useColorModeValue('gray.100', 'gray.700');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!input.trim()) return;

        // Add user message
        const userMessage: Message = {
            id: `user-${Date.now()}`,
            text: input,
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');

        try {
            // In a real implementation, this would call the backend API
            // For now, we'll simulate a response
            setTimeout(() => {
                const assistantMessage: Message = {
                    id: `assistant-${Date.now()}`,
                    text: `This is a placeholder response to: "${input}"`,
                    sender: 'assistant',
                    timestamp: new Date(),
                };
                setMessages((prev) => [...prev, assistantMessage]);
            }, 1000);
        } catch (error) {
            console.error('Failed to get response:', error);
        }
    };

    return (
        <Box>
            <VStack spacing={4} align="stretch" h="60vh">
                <Box flex="1" overflowY="auto" p={2}>
                    {messages.length === 0 ? (
                        <Flex h="100%" align="center" justify="center">
                            <Text color="gray.500">Start a conversation</Text>
                        </Flex>
                    ) : (
                        messages.map((message) => (
                            <Box
                                key={message.id}
                                bg={message.sender === 'user' ? userBgColor : assistantBgColor}
                                p={3}
                                borderRadius="md"
                                my={2}
                                maxW="80%"
                                alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                                ml={message.sender === 'user' ? 'auto' : 0}
                            >
                                <Text>{message.text}</Text>
                                <Text fontSize="xs" color="gray.500" mt={1}>
                                    {message.timestamp.toLocaleTimeString()}
                                </Text>
                            </Box>
                        ))
                    )}
                </Box>
            </VStack>

            <Box as="form" onSubmit={handleSubmit} mt={4}>
                <HStack>
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        size="md"
                    />
                    <Button type="submit" colorScheme="brand">
                        Send
                    </Button>
                </HStack>
            </Box>
        </Box>
    );
};
