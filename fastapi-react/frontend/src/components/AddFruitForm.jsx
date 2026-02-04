import React, { useState } from 'react';

const AddFruitForm = ({ addFruit }) => {
  const [fruitName, setFruitName] = useState('');
  const [fruitCategory, setFruitCategory] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (fruitName) {
      addFruit(fruitName, fruitCategory);
      setFruitName('');
      setFruitCategory('');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={fruitName}
        onChange={(e) => setFruitName(e.target.value)}
        placeholder="Enter fruit name"
      />
       <input
        type="text"
        value={fruitCategory}
        onChange={(e) => setFruitCategory(e.target.value)}
        placeholder="Enter fruit category"
      />
      <button type="submit">Add Fruit</button>
    </form>
  );
};

export default AddFruitForm;