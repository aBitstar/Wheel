import {
    Button,
    Container,
    Text,
    Heading,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalFooter,
    ModalHeader,
    ModalOverlay,
    VStack,
    StackDivider,
  } from "@chakra-ui/react"
  import { useMutation, useQueryClient } from "@tanstack/react-query"
  import { type SubmitHandler, useForm } from "react-hook-form"
  
  import {
    type ApiError,
    type UserPublic,
    type UserUpdate,
    UsersService,
  } from "../../client"
  import useCustomToast from "../../hooks/useCustomToast"
  
  interface EditUserProps {
    user: UserPublic
    isOpen: boolean
    onClose: () => void
  }
  
  interface UserUpdateForm extends UserUpdate {
    confirm_password: string
  }
  
  const ViewUser = ({ user, isOpen, onClose }: EditUserProps) => {
    const queryClient = useQueryClient()
    const showToast = useCustomToast()

  
    const {
      register,
      handleSubmit,
      reset,
      getValues,
      formState: { errors, isSubmitting, isDirty },
    } = useForm<UserUpdateForm>({
      mode: "onBlur",
      criteriaMode: "all",
      defaultValues: user,
    })
  
    const mutation = useMutation({
      mutationFn: (data: UserUpdateForm) =>
        UsersService.updateUser({ userId: user.id, requestBody: data }),
      onSuccess: () => {
        showToast("Success!", "User updated successfully.", "success")
        onClose()
      },
      onError: (err: ApiError) => {
        const errDetail = (err.body as any)?.detail
        showToast("Something went wrong.", `${errDetail}`, "error")
      },
      onSettled: () => {
        queryClient.invalidateQueries({ queryKey: ["users"] })
      },
    })
  
    const onSubmit: SubmitHandler<UserUpdateForm> = async (data) => {
      if (data.password === "") {
        data.password = undefined
      }
      mutation.mutate(data)
    }
  
    const onCancel = () => {
      reset()
      onClose()
    }
  
    return (
      <>
        <Modal
          isOpen={isOpen}
          onClose={onClose}
          size={{ base: "sm", md: "md" }}
          isCentered
        >
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>User Information</ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
                <VStack
                    divider={<StackDivider borderColor='gray.200' />}
                    spacing={4}
                    align='stretch'
                >
                    <Container>
                        <Heading as='h2' size='sm'>User Name</Heading>
                        <Text fontSize='xl'>{user.full_name}</Text>
                    </Container>
                    <Container>
                        <Heading as='h2' size='sm'>User Email</Heading>
                        <Text fontSize='xl'>{user.email}</Text>
                    </Container>
                    <Container>
                        <Heading as='h2' size='sm'>User Role</Heading>
                        <Text fontSize='xl'>{user.is_superuser ? 'Admin' : 'User'}</Text>
                    </Container>
                </VStack>
            </ModalBody>
  
            <ModalFooter gap={3}>
              <Button
                variant="primary"
                type="submit"
                isLoading={isSubmitting}
              >
                Send Friend Request
              </Button>
              <Button onClick={onCancel}>Cancel</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </>
    )
  }
  
  export default ViewUser
  