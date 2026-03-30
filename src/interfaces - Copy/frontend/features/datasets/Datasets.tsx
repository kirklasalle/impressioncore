import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Flex,
    Heading,
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    Input,
    InputGroup,
    InputLeftElement,
    useToast,
    Spinner,
    Text,
} from '@chakra-ui/react';
import { FaSearch, FaPlus } from 'react-icons/fa';
import { useApi } from '../../hooks/useApi';

interface Dataset {
    id: string;
    name: string;
    description: string;
    recordCount: number;
    createdAt: string;
}

export const Datasets: React.FC = () => {
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const toast = useToast();
    const api = useApi();

    useEffect(() => {
        const fetchDatasets = async () => {
            try {
                setIsLoading(true);
                // In a complete implementation, this would use the actual API client
                // For now, we'll simulate API data
                setTimeout(() => {
                    const mockDatasets: Dataset[] = [
                        {
                            id: '1',
                            name: 'Customer Support Conversations',
                            description: 'Dataset containing customer support conversations',
                            recordCount: 10000,
                            createdAt: '2023-04-15T10:30:00Z',
                        },
                        {
                            id: '2',
                            name: 'Medical Research Papers',
                            description: 'Collection of medical research papers for training',
                            recordCount: 5000,
                            createdAt: '2023-05-20T14:45:00Z',
                        },
                        {
                            id: '3',
                            name: 'Code Documentation',
                            description: 'Programming documentation and tutorials',
                            recordCount: 8000,
                            createdAt: '2023-06-10T09:15:00Z',
                        },
                    ];
                    setDatasets(mockDatasets);
                    setIsLoading(false);
                }, 800);
            } catch (error) {
                console.error('Failed to fetch datasets:', error);
                toast({
                    title: 'Error fetching datasets',
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                });
                setIsLoading(false);
            }
        };

        fetchDatasets();
    }, [toast]);

    const filteredDatasets = datasets.filter(dataset =>
        dataset.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        dataset.description.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <Box>
            <Flex justify="space-between" align="center" mb={6}>
                <Heading size="md">Datasets</Heading>
                <Button leftIcon={<FaPlus />} colorScheme="brand" size="sm">
                    Create Dataset
                </Button>
            </Flex>

            <InputGroup mb={6}>
                <InputLeftElement pointerEvents="none">
                    <FaSearch color="gray.300" />
                </InputLeftElement>
                <Input
                    placeholder="Search datasets..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
            </InputGroup>

            {isLoading ? (
                <Flex justify="center" align="center" height="200px">
                    <Spinner size="xl" color="brand.500" />
                </Flex>
            ) : filteredDatasets.length > 0 ? (
                <Table variant="simple">
                    <Thead>
                        <Tr>
                            <Th>Name</Th>
                            <Th>Description</Th>
                            <Th isNumeric>Records</Th>
                            <Th>Created</Th>
                        </Tr>
                    </Thead>
                    <Tbody>
                        {filteredDatasets.map((dataset) => (
                            <Tr key={dataset.id} _hover={{ bg: 'gray.50' }} cursor="pointer">
                                <Td fontWeight="medium">{dataset.name}</Td>
                                <Td>{dataset.description}</Td>
                                <Td isNumeric>{dataset.recordCount.toLocaleString()}</Td>
                                <Td>{new Date(dataset.createdAt).toLocaleDateString()}</Td>
                            </Tr>
                        ))}
                    </Tbody>
                </Table>
            ) : (
                <Flex justify="center" align="center" height="200px">
                    <Text color="gray.500">No datasets found</Text>
                </Flex>
            )}
        </Box>
    );
};
