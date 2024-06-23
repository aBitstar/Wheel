import { Button, Stack } from "@chakra-ui/react"
const RequestActions = () => {
    return (
        <Stack direction={"row"} spacing={4} align="center">
            <Button colorScheme="blue" variant="solid" >Accept</Button>
            <Button colorScheme="red" variant="solid" >Decline</Button>
        </Stack>
    )
}

export default RequestActions