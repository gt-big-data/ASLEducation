import React from 'react';
import { ChakraProvider, Heading, Box, Text, Flex } from '@chakra-ui/react';

const teamMembers = [
    { name: 'Advay Balakrishnan', role: 'Analysis'},
    { name: 'Joshua Diao', role: 'Analysis'},
    { name: 'Erel Ozen', role: 'Data Viz'},
    { name: 'Pranav Somu', role: 'Analysis'}
];

const TeamMember = ({ name, role }) => (
    <Box p={4} shadow="md" borderWidth="1px" borderRadius="md">
        <Heading as="h3" size="md">{name}</Heading>
        <Text mt={2} color="blue.300">{role}</Text>
    </Box>
)

const OurTeam = () => {
    console.log("OurTeam component rendered!"); // Check if component is rendered
    return (
        <ChakraProvider>
            <Box p={8}>
                <Heading size="xl" mb={4}>Meet the Team</Heading>
                <Flex flexWrap="wrap">
                    {teamMembers.map((member, index) => (
                        <TeamMember key={index} name={member.name} role={member.role} />
                    ))}
                </Flex>
            </Box>
        </ChakraProvider>
    )
};

export default OurTeam;
