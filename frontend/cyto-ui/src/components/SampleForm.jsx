import React, { useState } from "react";

export default function SampleForm({ onSuccess }) {
  const [form, setForm] = useState({
    sample_id: "",
    subject_id: "",
    treatment: "",
    response: "",
    sample_type: "",
    time_from_treatment_start: 0,
    project: "",
    condition: "",
    age: 0,
    sex: "",
    cell_counts: {
      b_cell: 0,
      cd4_t_cell: 0,
      cd8_t_cell: 0,
      nk_cell: 0,
      monocyte: 0,
    },
  });

  const validateForm = () => {
    const requiredFields = [
      "sample_id", "subject_id", "treatment", "sample_type", "project", "condition", "age", "sex"
    ];

    for (let field of requiredFields) {
      if (!form[field]) {
        alert(`Field "${field}" is required.`);
        return false;
      }
    }

    // no negative integers
    if (form.age < 0 || form.time_from_treatment_start < 0) {
      alert("Age and Time from Treatment Start must be non-negative.");
      return false;
    }

    for (let count of Object.values(form.cell_counts)) {
      if (count < 0) {
        alert("All cell counts must be non-negative.");
        return false;
      }
    }

    // sum(cell_counts) > 0 (to avoid div by zero errors with relative_freq calculation)
    const sumValues = Object.values(form.cell_counts).reduce((a, b) => a + b, 0);
    if (sumValues <= 0) {
      alert("All cell counts cannot be zero.");
      return false;
    }

    return true;
  }

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name in form.cell_counts) {
      setForm({
        ...form,
        cell_counts: { ...form.cell_counts, [name]: parseInt(value) || 0 },
      });
    } else {
      setForm({ ...form, [name]: value });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    const res = await fetch("/samples", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    if (res.ok) {
      setForm({ ...form, sample_id: "" });
      onSuccess();
    }
  };

  const handleDelete = async (e) => {
    e.preventDefault();

    // only sample id required
    if (!form.sample_id) {
      alert("Sample ID required for deletion.");
      return;
    }

    const res = await fetch(`/samples/${form.sample_id}`, { method: "DELETE" });
    if (res.ok) {
      setForm({ ...form, sample_id: "" });
      onSuccess();
    }
  };

  return (
    <form className="max-w-sm" onSubmit={handleSubmit}>
      <div>
        <label className="block font-bold mb-2">Sample ID: </label>
        <input className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight" name="sample_id" value={form.sample_id} onChange={handleChange} required />
      </div>
      <div>
        <label className="block font-bold mb-2">Subject ID: </label>
        <input className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight" name="subject_id" value={form.subject_id} onChange={handleChange} required />
      </div>
      <div>
        <label className="block font-bold mb-2">Treatment: </label>
        <input className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight" name="treatment" value={form.treatment} onChange={handleChange} />
      </div>
      <div>
        <label className="block font-bold mb-2">Response: </label>
        <select
          className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight"
          name="response"
          value={form.response}
          onChange={handleChange}
        >
          <option value="">Select a response</option>
          <option value="y">Yes</option>
          <option value="n">No</option>
        </select>
      </div>
      <div>
        <label className="block font-bold mb-2">Sample Type: </label>
        <input className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight" name="sample_type" value={form.sample_type} onChange={handleChange} />
      </div>
      <div>
        <label className="block font-bold mb-2">Time from Treatment Start: </label>
        <input className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight" name="time_from_treatment_start" type="number" value={form.time_from_treatment_start} onChange={handleChange} />
      </div>
      <div>
        <label className="block font-bold mb-2">Project: </label>
        <input className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight" name="project" value={form.project} onChange={handleChange} />
      </div>
      <div>
        <label className="block font-bold mb-2">Condition: </label>
        <input className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight" name="condition" value={form.condition} onChange={handleChange} />
      </div>
      <div>
        <label className="block font-bold mb-2">Age: </label>
        <input className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight" name="age" type="number" value={form.age} onChange={handleChange} />
      </div>
      <div>
        <label className="block font-bold mb-2">Sex: </label>
        <select
          className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight"
          name="sex"
          value={form.sex}
          onChange={handleChange}
        >
          <option value="">Select sex</option>
          <option value="M">Male</option>
          <option value="F">Female</option>
        </select>
      </div>

      <fieldset>
        <legend className="font-bold text-lg py-2">Cell Counts:</legend>
        {Object.entries(form.cell_counts).map(([key, val]) => (
          <div key={key}>
            <label className="font-bold mb-2">{key}: </label>
            <input className="shadow appearance-none border rounded w-full py-2 px-3 leading-tight focus:outline-none focus:shadow-outline" name={key} type="number" value={val} onChange={handleChange} />
          </div>
        ))}
      </fieldset>

      <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 m-2" type="submit">Add Sample</button>
      <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 m-2" type="button" onClick={handleDelete}>Delete Sample</button>
    </form>
  );
}