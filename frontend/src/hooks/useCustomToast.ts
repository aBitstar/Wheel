import { AlertStatus, useToast } from "@chakra-ui/react"
import { useCallback } from "react"

const useCustomToast = () => {
  const toast = useToast()

  const showToast = useCallback(
    (title: string, description: string, status: AlertStatus) => {
      toast({
        title,
        description,
        status,
        isClosable: true,
        position: "bottom-right",
      })
    },
    [toast],
  )

  return showToast
}

export default useCustomToast
