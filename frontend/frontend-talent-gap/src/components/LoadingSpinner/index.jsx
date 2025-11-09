import ClipLoader from 'react-spinners/ClipLoader';

const LoadingSpinner = ({ color = '#4A90E2', size = 50, loadText }) => {
  const override = {
    display: 'block',
    margin: '0 auto',
    borderColor: color, 
  };

  return (
    <div class="sweet-loading">
      <ClipLoader
        color={color}
        loading={true}
        cssOverride={override}
        size={size}
        aria-label="Loading Spinner"
        data-testid="loader"
      />
      <p>{loadText}</p>
    </div>
  );
};

export default LoadingSpinner;