import { Button, Stack } from "@chakra-ui/react"
const RequestActions = ({onAccept, onDecline}) => {
    return (
        <Stack direction={"row"} spacing={4} align="center">
            <Button colorScheme="blue" variant="solid" onClick={() => onAccept()}>Accept</Button>
            <Button colorScheme="red" variant="solid" onClick={() => onDecline()}>Decline</Button>
        </Stack>
    )
}

export default RequestActions