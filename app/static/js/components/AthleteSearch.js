const AthleteSearch = () => {
  const [query, setQuery] = React.useState('');
  const [suggestions, setSuggestions] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [showDropdown, setShowDropdown] = React.useState(false);
  const searchRef = React.useRef(null);

  React.useEffect(() => {
      // Handle clicks outside of the search component
      const handleClickOutside = (event) => {
          if (searchRef.current && !searchRef.current.contains(event.target)) {
              setShowDropdown(false);
          }
      };

      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const debounce = (func, wait) => {
      let timeout;
      return (...args) => {
          clearTimeout(timeout);
          timeout = setTimeout(() => func.apply(this, args), wait);
      };
  };

  const fetchSuggestions = async (searchTerm) => {
      if (searchTerm.length < 2) {
          setSuggestions([]);
          return;
      }

      setIsLoading(true);
      try {
          const response = await fetch(`/api/search-players?q=${encodeURIComponent(searchTerm)}`);
          const data = await response.json();
          setSuggestions(data);
          setShowDropdown(true);
      } catch (error) {
          console.error('Error fetching suggestions:', error);
          setSuggestions([]);
      } finally {
          setIsLoading(false);
      }
  };

  const debouncedFetch = React.useMemo(
      () => debounce(fetchSuggestions, 300),
      []
  );

  const handleInputChange = (e) => {
      const value = e.target.value;
      setQuery(value);
      debouncedFetch(value);
  };

  const handleSelectAthlete = (athlete) => {
      window.location.href = `/dashboard/player/${athlete.id}`;
  };

  return React.createElement('div', { 
      className: 'w-full max-w-2xl mx-auto',
      ref: searchRef 
  }, [
      React.createElement('div', { 
          key: 'search-container',
          className: 'relative' 
      }, [
          React.createElement('div', { 
              key: 'input-container',
              className: 'relative' 
          }, [
              React.createElement('input', {
                  key: 'search-input',
                  type: 'text',
                  className: 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                  placeholder: 'Search athletes...',
                  value: query,
                  onChange: handleInputChange,
                  onFocus: () => query.length >= 2 && setShowDropdown(true)
              }),
              isLoading && React.createElement('div', {
                  key: 'loading-spinner',
                  className: 'absolute right-3 top-2'
              }, [
                  React.createElement('div', {
                      key: 'spinner',
                      className: 'animate-spin h-5 w-5 border-2 border-blue-500 rounded-full border-t-transparent'
                  })
              ])
          ]),
          showDropdown && suggestions.length > 0 && React.createElement('div', {
              key: 'suggestions-dropdown',
              className: 'absolute w-full mt-1 bg-white border rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto'
          }, suggestions.map(athlete => 
              React.createElement('div', {
                  key: athlete.id,
                  className: 'px-4 py-2 hover:bg-gray-100 cursor-pointer transition-colors',
                  onClick: () => handleSelectAthlete(athlete)
              }, [
                  React.createElement('div', {
                      key: 'name',
                      className: 'font-medium'
                  }, `${athlete.firstname} ${athlete.lastname}`),
                  athlete.school && React.createElement('div', {
                      key: 'school',
                      className: 'text-sm text-gray-600'
                  }, athlete.school)
              ])
          )),
          showDropdown && query.length >= 2 && suggestions.length === 0 && React.createElement('div', {
              key: 'no-results',
              className: 'absolute w-full mt-1 bg-white border rounded-lg shadow-lg z-10 p-4 text-center text-gray-500'
          }, 'No athletes found')
      ])
  ]);
};