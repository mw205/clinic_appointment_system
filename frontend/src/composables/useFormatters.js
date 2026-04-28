export const useFormatters = () => {
  function formatTime(timestamp)
  {
    return new Date(timestamp).toLocaleTimeString()
  }

  return{
    formatTime
  }
}
